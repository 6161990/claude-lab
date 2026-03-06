package com.oneonone.service

import com.oneonone.config.JiraProperties
import com.oneonone.dto.*
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Qualifier
import org.springframework.stereotype.Service
import org.springframework.web.client.RestClient
import org.springframework.web.client.RestClientException
import org.springframework.web.util.UriComponentsBuilder
import java.time.LocalDate

/**
 * Jira Cloud REST API 서비스
 * 이슈 조회, 프로젝트 목록, Confluence 페이지 조회, 회고 생성을 담당
 */
@Service
class JiraService(
    private val jiraProperties: JiraProperties,
    @Qualifier("jiraRestClient") private val restClient: RestClient
) {
    private val log = LoggerFactory.getLogger(JiraService::class.java)

    // ============================================================
    // 연결 상태 확인
    // ============================================================

    /**
     * Jira 연결 상태 확인 (현재 사용자 정보 조회)
     */
    fun checkConnection(): JiraStatusResponse {
        if (!jiraProperties.enabled || jiraProperties.baseUrl.isBlank()) {
            return JiraStatusResponse(
                connected = false,
                message = "Jira 연동이 비활성화되어 있습니다. 환경변수를 설정해주세요."
            )
        }

        return try {
            val myself = restClient.get()
                .uri("/rest/api/3/myself")
                .retrieve()
                .body(JiraMyself::class.java)!!

            JiraStatusResponse(
                connected = true,
                message = "Jira 연결 성공",
                accountId = myself.accountId,
                displayName = myself.displayName,
                email = myself.emailAddress
            )
        } catch (e: RestClientException) {
            log.error("Jira 연결 실패: ${e.message}")
            JiraStatusResponse(connected = false, message = "연결 실패: ${e.message}")
        }
    }

    // ============================================================
    // Jira 이슈 조회 (JQL 기반)
    // ============================================================

    /**
     * JQL로 이슈 검색
     */
    fun searchIssues(
        jql: String,
        startAt: Int = 0,
        maxResults: Int = 50
    ): JiraIssuesResponse {
        requireJiraEnabled()
        log.debug("Jira 이슈 검색: jql=$jql")

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

    /**
     * 현재 API 토큰 사용자의 이슈 조회
     */
    fun getMyIssues(projectKey: String? = null, quarter: String? = null): JiraIssuesResponse {
        val jql = buildAssigneeJql("currentUser()", projectKey, quarter, statusFilter = null)
        return searchIssues(jql, maxResults = 100)
    }

    /**
     * 현재 API 토큰 사용자의 완료 이슈
     */
    fun getDoneIssues(projectKey: String? = null, quarter: String? = null): JiraIssuesResponse {
        val jql = buildAssigneeJql("currentUser()", projectKey, quarter, statusFilter = "Done", useResolutionDate = true)
        return searchIssues(jql, maxResults = 100)
    }

    /**
     * 현재 API 토큰 사용자의 진행 중 이슈
     */
    fun getInProgressIssues(projectKey: String? = null): JiraIssuesResponse {
        val conditions = mutableListOf("assignee = currentUser()", "statusCategory != Done")
        if (projectKey != null) conditions.add("project = $projectKey")
        return searchIssues(conditions.joinToString(" AND ") + " ORDER BY updated DESC", maxResults = 50)
    }

    /**
     * 스프린트 이슈 조회
     */
    fun getSprintIssues(sprintName: String): JiraIssuesResponse {
        val jql = "assignee = currentUser() AND sprint = \"$sprintName\" ORDER BY status ASC"
        return searchIssues(jql, maxResults = 100)
    }

    // ============================================================
    // 이메일 기반 회고 생성 (핵심 신규 기능)
    // ============================================================

    /**
     * 이메일로 특정 사용자의 회고 데이터 생성
     * 클라이언트에서 email + quarter만 넘기면 Jira/Confluence 데이터를 통합하여 반환
     *
     * @param request email, quarter, projectKey(optional), spaceKey(optional)
     */
    fun generateRetrospectiveByEmail(request: JiraRetrospectiveRequest): RetrospectiveJiraResponse {
        requireJiraEnabled()
        log.info("이메일 기반 회고 생성: email=${request.email}, quarter=${request.quarter}")

        // 완료 이슈 (Done + 해당 분기 내 resolve)
        val doneJql = buildAssigneeJql(
            assignee = "\"${request.email}\"",
            projectKey = request.projectKey,
            quarter = request.quarter,
            statusFilter = "Done",
            useResolutionDate = true
        )
        val doneIssues = searchIssues(doneJql, maxResults = 100)

        // 진행 중 이슈 (Done 아닌 것 전체)
        val inProgressConditions = mutableListOf(
            "assignee = \"${request.email}\"",
            "statusCategory != Done"
        )
        if (request.projectKey != null) inProgressConditions.add("project = ${request.projectKey}")
        val inProgressJql = inProgressConditions.joinToString(" AND ") + " ORDER BY updated DESC"
        val inProgressIssues = searchIssues(inProgressJql, maxResults = 50)

        // Confluence 페이지 (spaceKey 있을 경우)
        val confluencePages = if (request.spaceKey != null) {
            getConfluencePages(request.spaceKey, quarter = request.quarter)
        } else {
            ConfluencePagesResponse(emptyList(), 0)
        }

        return RetrospectiveJiraResponse(
            quarter = request.quarter,
            doneIssues = doneIssues.issues,
            inProgressIssues = inProgressIssues.issues,
            confluencePages = confluencePages.pages,
            totalDone = doneIssues.total,
            totalInProgress = inProgressIssues.total
        )
    }

    /**
     * 현재 API 토큰 사용자의 회고 종합 데이터 (currentUser() 기반)
     */
    fun getRetrospectiveData(
        quarter: String,
        projectKey: String? = null,
        spaceKey: String? = null
    ): RetrospectiveJiraResponse {
        val doneIssues = getDoneIssues(projectKey, quarter)
        val inProgressIssues = getInProgressIssues(projectKey)
        val confluencePages = if (spaceKey != null) {
            getConfluencePages(spaceKey, quarter = quarter)
        } else {
            ConfluencePagesResponse(emptyList(), 0)
        }

        return RetrospectiveJiraResponse(
            quarter = quarter,
            doneIssues = doneIssues.issues,
            inProgressIssues = inProgressIssues.issues,
            confluencePages = confluencePages.pages,
            totalDone = doneIssues.total,
            totalInProgress = inProgressIssues.total
        )
    }

    // ============================================================
    // 프로젝트 목록
    // ============================================================

    fun getProjects(): List<JiraProjectRaw> {
        requireJiraEnabled()
        return restClient.get()
            .uri("/rest/api/3/project")
            .retrieve()
            .body(Array<JiraProjectRaw>::class.java)
            ?.toList() ?: emptyList()
    }

    // ============================================================
    // Confluence 페이지 조회
    // ============================================================

    fun getConfluencePages(
        spaceKey: String,
        limit: Int = 25,
        quarter: String? = null
    ): ConfluencePagesResponse {
        requireJiraEnabled()
        log.debug("Confluence 페이지 조회: spaceKey=$spaceKey, quarter=$quarter")

        val uriBuilder = UriComponentsBuilder.fromPath("/wiki/rest/api/content")
            .queryParam("type", "page")
            .queryParam("spaceKey", spaceKey)
            .queryParam("limit", limit)
            .queryParam("expand", "history,history.lastUpdated,space")
            .queryParam("orderby", "history.lastUpdated desc")

        val raw = restClient.get()
            .uri(uriBuilder.build().toUriString())
            .retrieve()
            .body(ConfluenceSearchResponse::class.java)!!

        return ConfluencePagesResponse(
            pages = raw.results.map { it.toResponse(jiraProperties.baseUrl) },
            total = raw.size
        )
    }

    // ============================================================
    // 유틸리티
    // ============================================================

    /**
     * assignee 기반 JQL 조건 빌더
     * @param assignee "currentUser()" 또는 "\"email@domain.com\""
     * @param useResolutionDate true면 resolutiondate, false면 updated 기준 날짜 필터
     */
    private fun buildAssigneeJql(
        assignee: String,
        projectKey: String?,
        quarter: String?,
        statusFilter: String?,
        useResolutionDate: Boolean = false
    ): String {
        val conditions = mutableListOf("assignee = $assignee")

        if (statusFilter != null) conditions.add("status = $statusFilter")
        if (projectKey != null) conditions.add("project = $projectKey")

        if (quarter != null) {
            val (startDate, endDate) = getQuarterDateRange(quarter)
            val dateField = if (useResolutionDate) "resolutiondate" else "updated"
            conditions.add("$dateField >= \"$startDate\"")
            conditions.add("$dateField <= \"$endDate\"")
        }

        val orderBy = if (useResolutionDate) "resolutiondate" else "updated"
        return conditions.joinToString(" AND ") + " ORDER BY $orderBy DESC"
    }

    /**
     * 분기별 날짜 범위 반환 (yyyy-MM-dd 형식)
     */
    private fun getQuarterDateRange(quarter: String): Pair<String, String> {
        val year = LocalDate.now().year
        return when (quarter.uppercase()) {
            "Q1" -> "$year-01-01" to "$year-03-31"
            "Q2" -> "$year-04-01" to "$year-06-30"
            "Q3" -> "$year-07-01" to "$year-09-30"
            "Q4" -> "$year-10-01" to "$year-12-31"
            else -> throw IllegalArgumentException("유효하지 않은 분기: $quarter (Q1~Q4만 허용)")
        }
    }

    private fun requireJiraEnabled() {
        if (!jiraProperties.enabled) {
            throw IllegalStateException("Jira 연동이 비활성화되어 있습니다. JIRA_ENABLED=true 환경변수를 설정해주세요.")
        }
        if (jiraProperties.baseUrl.isBlank() || jiraProperties.apiToken.isBlank()) {
            throw IllegalStateException("Jira 설정이 불완전합니다. JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN 환경변수를 확인해주세요.")
        }
    }
}

// ============================================================
// 확장 함수 (raw API 응답 → 클라이언트 응답 DTO 변환)
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
