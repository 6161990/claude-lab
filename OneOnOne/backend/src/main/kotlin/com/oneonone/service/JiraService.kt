package com.oneonone.service

import com.oneonone.config.JiraProperties
import com.oneonone.dto.*
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Qualifier
import org.springframework.stereotype.Service
import org.springframework.web.client.RestClient
import org.springframework.web.client.RestClientException
import org.springframework.web.util.UriComponentsBuilder

@Service
class JiraService(
    private val jiraProperties: JiraProperties,
    @Qualifier("jiraRestClient") private val restClient: RestClient
) {
    private val log = LoggerFactory.getLogger(JiraService::class.java)

    // ============================================================
    // 핵심: 이메일 기반 회고 데이터 생성 (날짜 범위)
    // ============================================================

    /**
     * 지정 기간 내 특정 사용자의 Jira 이슈 + Confluence 기여 페이지를 통합 반환합니다.
     */
    fun generateRetrospectiveByEmail(request: JiraRetrospectiveRequest): RetrospectiveJiraResponse {
        requireJiraEnabled()
        log.info("회고 생성: email=${request.email}, ${request.startDate} ~ ${request.endDate}")

        // 완료된 이슈 (기간 내 resolutiondate 기준)
        val doneJql = buildJql(
            assignee = "\"${request.email}\"",
            startDate = request.startDate,
            endDate = request.endDate,
            statusFilter = "Done",
            dateField = "resolutiondate",
            projectKey = request.projectKey
        )
        val doneIssues = searchIssues(doneJql, maxResults = 100)

        // 진행 중 이슈 (Done 아닌 것, 기간 내 updated)
        val inProgressConditions = mutableListOf(
            "assignee = \"${request.email}\"",
            "statusCategory != Done",
            "updated >= \"${request.startDate}\"",
            "updated <= \"${request.endDate}\""
        )
        if (request.projectKey != null) inProgressConditions.add("project = ${request.projectKey}")
        val inProgressIssues = searchIssues(
            inProgressConditions.joinToString(" AND ") + " ORDER BY updated DESC",
            maxResults = 50
        )

        // Confluence 기여 페이지 (생성 또는 편집)
        val confluencePages = getContributedPages(
            email = request.email,
            startDate = request.startDate,
            endDate = request.endDate
        )

        return RetrospectiveJiraResponse(
            startDate = request.startDate,
            endDate = request.endDate,
            doneIssues = doneIssues.issues,
            inProgressIssues = inProgressIssues.issues,
            confluencePages = confluencePages.pages,
            totalDone = doneIssues.total,
            totalInProgress = inProgressIssues.total
        )
    }

    // ============================================================
    // Jira 이슈 검색
    // ============================================================

    fun searchIssues(jql: String, startAt: Int = 0, maxResults: Int = 50): JiraIssuesResponse {
        requireJiraEnabled()

        val fields = "summary,status,assignee,reporter,priority,issuetype,project,created,updated,resolutiondate,labels"
        val uri = UriComponentsBuilder.fromPath("/rest/api/3/search")
            .queryParam("jql", jql)
            .queryParam("startAt", startAt)
            .queryParam("maxResults", maxResults)
            .queryParam("fields", fields)
            .build().toUriString()

        val raw = restClient.get().uri(uri).retrieve().body(JiraSearchResponse::class.java)!!

        return JiraIssuesResponse(
            issues = raw.issues.map { it.toResponse(jiraProperties.baseUrl) },
            total = raw.total,
            maxResults = raw.maxResults,
            startAt = raw.startAt
        )
    }

    // ============================================================
    // Confluence 기여 페이지 (생성 또는 편집)
    // ============================================================

    /**
     * 특정 사용자가 지정 기간 내 생성하거나 편집한 Confluence 페이지를 반환합니다.
     * Jira accountId를 먼저 조회한 뒤 Confluence CQL contributor 필터에 활용합니다.
     */
    fun getContributedPages(
        email: String,
        startDate: String,
        endDate: String,
        limit: Int = 50
    ): ConfluencePagesResponse {
        if (!jiraProperties.enabled) return ConfluencePagesResponse(emptyList(), 0)

        return try {
            val accountId = resolveAccountId(email)
            val cql = if (accountId != null) {
                "type = page AND contributor.accountid = \"$accountId\" " +
                        "AND lastModified >= \"$startDate\" AND lastModified <= \"$endDate\""
            } else {
                log.warn("accountId 조회 실패 ($email), 날짜 범위로만 검색합니다.")
                "type = page AND lastModified >= \"$startDate\" AND lastModified <= \"$endDate\""
            }

            val uri = UriComponentsBuilder.fromPath("/wiki/rest/api/search")
                .queryParam("cql", cql)
                .queryParam("limit", limit)
                .queryParam("expand", "history,history.lastUpdated,space")
                .build().toUriString()

            val raw = restClient.get().uri(uri).retrieve()
                .body(ConfluenceSearchResponse::class.java)!!

            ConfluencePagesResponse(
                pages = raw.results.map { it.toResponse(jiraProperties.baseUrl) },
                total = raw.size
            )
        } catch (e: Exception) {
            log.warn("Confluence 페이지 조회 실패: ${e.message}")
            ConfluencePagesResponse(emptyList(), 0)
        }
    }

    // ============================================================
    // 유틸리티
    // ============================================================

    /**
     * 이메일로 Jira accountId를 조회합니다.
     */
    private fun resolveAccountId(email: String): String? {
        return try {
            val users = restClient.get()
                .uri("/rest/api/3/user/search?query=$email&maxResults=1")
                .retrieve()
                .body(Array<JiraMyself>::class.java)
            users?.firstOrNull()?.accountId
        } catch (e: RestClientException) {
            log.warn("accountId 조회 실패: ${e.message}")
            null
        }
    }

    private fun buildJql(
        assignee: String,
        startDate: String,
        endDate: String,
        statusFilter: String? = null,
        dateField: String = "updated",
        projectKey: String? = null
    ): String {
        val conditions = mutableListOf("assignee = $assignee")
        if (statusFilter != null) conditions.add("status = $statusFilter")
        if (projectKey != null) conditions.add("project = $projectKey")
        conditions.add("$dateField >= \"$startDate\"")
        conditions.add("$dateField <= \"$endDate\"")
        return conditions.joinToString(" AND ") + " ORDER BY $dateField DESC"
    }

    private fun requireJiraEnabled() {
        if (!jiraProperties.enabled)
            throw IllegalStateException("Jira 연동이 비활성화되어 있습니다. JIRA_ENABLED=true 환경변수를 설정해주세요.")
        if (jiraProperties.baseUrl.isBlank() || jiraProperties.apiToken.isBlank())
            throw IllegalStateException("Jira 설정이 불완전합니다. JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN을 확인해주세요.")
    }

    fun checkConnection(): JiraStatusResponse {
        if (!jiraProperties.enabled || jiraProperties.baseUrl.isBlank()) {
            return JiraStatusResponse(connected = false, message = "Jira 연동이 비활성화되어 있습니다.")
        }
        return try {
            val myself = restClient.get().uri("/rest/api/3/myself").retrieve().body(JiraMyself::class.java)!!
            JiraStatusResponse(connected = true, message = "연결 성공", accountId = myself.accountId, displayName = myself.displayName, email = myself.emailAddress)
        } catch (e: RestClientException) {
            JiraStatusResponse(connected = false, message = "연결 실패: ${e.message}")
        }
    }
}

// ============================================================
// 확장 함수
// ============================================================

private fun JiraIssueRaw.toResponse(baseUrl: String) = JiraIssueResponse(
    key = key,
    summary = fields.summary,
    status = fields.status.name,
    statusCategory = fields.status.statusCategory.key,
    issueType = fields.issuetype.name,
    project = fields.project.name,
    projectKey = fields.project.key,
    priority = fields.priority?.name ?: "없음",
    created = fields.created,
    updated = fields.updated,
    resolutionDate = fields.resolutiondate,
    labels = fields.labels,
    url = "$baseUrl/browse/$key"
)

private fun ConfluencePageRaw.toResponse(baseUrl: String) = ConfluencePageResponse(
    id = id,
    title = title,
    spaceKey = space.key,
    spaceName = space.name,
    lastUpdated = history.lastUpdated.`when`,
    lastUpdatedBy = history.lastUpdated.by.displayName,
    url = "$baseUrl/wiki${links.webui}"
)
