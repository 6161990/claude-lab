package com.oneonone.dto

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty

// ============================================================
// Jira 이슈 관련 DTO
// ============================================================

/**
 * Jira 이슈 검색 응답 (GET /rest/api/3/search)
 */
@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraSearchResponse(
    val issues: List<JiraIssueRaw> = emptyList(),
    val total: Int = 0,
    val maxResults: Int = 50,
    val startAt: Int = 0
)

/**
 * Jira 원본 이슈 응답 (API raw 형식)
 */
@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraIssueRaw(
    val id: String = "",
    val key: String = "",
    val fields: JiraIssueFields = JiraIssueFields()
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraIssueFields(
    val summary: String = "",
    val status: JiraStatus = JiraStatus(),
    val assignee: JiraUser? = null,
    val reporter: JiraUser? = null,
    val priority: JiraPriority? = null,
    val issuetype: JiraIssueType = JiraIssueType(),
    val project: JiraProject = JiraProject(),
    val created: String = "",
    val updated: String = "",
    val resolutiondate: String? = null,
    val labels: List<String> = emptyList()
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraStatus(
    val name: String = "",
    val statusCategory: JiraStatusCategory = JiraStatusCategory()
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraStatusCategory(
    val name: String = "",
    val key: String = ""
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraUser(
    val displayName: String = "",
    val emailAddress: String = "",
    val accountId: String = ""
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraPriority(
    val name: String = ""
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraIssueType(
    val name: String = "",
    val iconUrl: String = ""
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraProject(
    val key: String = "",
    val name: String = ""
)

// ============================================================
// 프로젝트 목록 DTO
// ============================================================

/**
 * Jira 프로젝트 목록 응답
 */
@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraProjectRaw(
    val id: String = "",
    val key: String = "",
    val name: String = "",
    val projectTypeKey: String = ""
)

// ============================================================
// 현재 사용자 정보 DTO
// ============================================================

@JsonIgnoreProperties(ignoreUnknown = true)
data class JiraMyself(
    val accountId: String = "",
    val displayName: String = "",
    val emailAddress: String = ""
)

// ============================================================
// Confluence 관련 DTO
// ============================================================

/**
 * Confluence 페이지 검색 응답 (GET /wiki/rest/api/content)
 */
@JsonIgnoreProperties(ignoreUnknown = true)
data class ConfluenceSearchResponse(
    val results: List<ConfluencePageRaw> = emptyList(),
    val size: Int = 0,
    val limit: Int = 25,
    val start: Int = 0
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class ConfluencePageRaw(
    val id: String = "",
    val title: String = "",
    val type: String = "",
    val space: ConfluenceSpace = ConfluenceSpace(),
    val history: ConfluenceHistory = ConfluenceHistory(),
    @JsonProperty("_links") val links: ConfluenceLinks = ConfluenceLinks()
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class ConfluenceSpace(
    val key: String = "",
    val name: String = ""
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class ConfluenceHistory(
    val createdDate: String = "",
    val lastUpdated: ConfluenceLastUpdated = ConfluenceLastUpdated()
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class ConfluenceLastUpdated(
    val `when`: String = "",
    val by: ConfluenceUser = ConfluenceUser()
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class ConfluenceUser(
    val displayName: String = "",
    val accountId: String = ""
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class ConfluenceLinks(
    val webui: String = ""
)

// ============================================================
// API 응답 DTO (컨트롤러에서 클라이언트로 반환)
// ============================================================

/**
 * 회고용 Jira 이슈 정리 응답
 */
data class JiraIssueResponse(
    val key: String,
    val summary: String,
    val status: String,
    val statusCategory: String,
    val issueType: String,
    val project: String,
    val projectKey: String,
    val priority: String,
    val created: String,
    val updated: String,
    val resolutionDate: String?,
    val labels: List<String>,
    val url: String
)

/**
 * 회고용 Confluence 페이지 정리 응답
 */
data class ConfluencePageResponse(
    val id: String,
    val title: String,
    val spaceKey: String,
    val spaceName: String,
    val lastUpdated: String,
    val lastUpdatedBy: String,
    val url: String
)

/**
 * Jira 이슈 목록 응답 (페이지네이션 포함)
 */
data class JiraIssuesResponse(
    val issues: List<JiraIssueResponse>,
    val total: Int,
    val maxResults: Int,
    val startAt: Int
)

/**
 * Confluence 페이지 목록 응답
 */
data class ConfluencePagesResponse(
    val pages: List<ConfluencePageResponse>,
    val total: Int
)

/**
 * Jira 연결 상태 확인 응답
 */
data class JiraStatusResponse(
    val connected: Boolean,
    val message: String,
    val accountId: String = "",
    val displayName: String = "",
    val email: String = ""
)

/**
 * 이메일 기반 회고 생성 요청
 */
data class JiraRetrospectiveRequest(
    val email: String,
    val startDate: String,   // yyyy-MM-dd
    val endDate: String,     // yyyy-MM-dd
    val projectKey: String? = null,
    val spaceKey: String? = null
)

/**
 * 회고 종합 응답 (Jira 이슈 + Confluence 페이지)
 */
data class RetrospectiveJiraResponse(
    val startDate: String,
    val endDate: String,
    val doneIssues: List<JiraIssueResponse>,
    val inProgressIssues: List<JiraIssueResponse>,
    val confluencePages: List<ConfluencePageResponse>,
    val totalDone: Int,
    val totalInProgress: Int
)
