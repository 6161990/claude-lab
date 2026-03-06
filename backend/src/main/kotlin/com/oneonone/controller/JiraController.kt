package com.oneonone.controller

import com.oneonone.dto.*
import com.oneonone.service.JiraService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

/**
 * Jira/Confluence 연동 REST API 컨트롤러
 * CORS는 WebConfig에서 전역 관리 (컨트롤러 @CrossOrigin 미사용)
 *
 * 엔드포인트:
 * - GET  /api/jira/status                   연결 상태 확인
 * - GET  /api/jira/issues                   JQL 검색
 * - GET  /api/jira/issues/mine              내가 담당한 이슈
 * - GET  /api/jira/issues/done              완료된 이슈
 * - GET  /api/jira/issues/in-progress       진행 중 이슈
 * - GET  /api/jira/issues/sprint            스프린트 이슈
 * - GET  /api/jira/retrospective            currentUser() 기반 회고
 * - POST /api/jira/retrospective            이메일 기반 회고 생성 (신규)
 * - GET  /api/jira/projects                 프로젝트 목록
 * - GET  /api/confluence/pages              Confluence 페이지 목록
 */
@RestController
@RequestMapping("/api")
class JiraController(private val jiraService: JiraService) {

    // ============================================================
    // 연결 상태
    // ============================================================

    @GetMapping("/jira/status")
    fun getStatus(): ResponseEntity<JiraStatusResponse> {
        val status = jiraService.checkConnection()
        return if (status.connected) ResponseEntity.ok(status)
        else ResponseEntity.status(503).body(status)
    }

    // ============================================================
    // Jira 이슈 조회
    // ============================================================

    /** JQL 직접 검색 */
    @GetMapping("/jira/issues")
    fun searchIssues(
        @RequestParam("jql") jql: String,
        @RequestParam("startAt", defaultValue = "0") startAt: Int,
        @RequestParam("maxResults", defaultValue = "50") maxResults: Int
    ): ResponseEntity<JiraIssuesResponse> =
        ResponseEntity.ok(jiraService.searchIssues(jql, startAt, maxResults))

    /** 내가 담당한 이슈 (currentUser()) */
    @GetMapping("/jira/issues/mine")
    fun getMyIssues(
        @RequestParam("quarter", required = false) quarter: String?,
        @RequestParam("project", required = false) project: String?
    ): ResponseEntity<JiraIssuesResponse> =
        ResponseEntity.ok(jiraService.getMyIssues(project, quarter))

    /** 완료된 이슈 */
    @GetMapping("/jira/issues/done")
    fun getDoneIssues(
        @RequestParam("quarter", required = false) quarter: String?,
        @RequestParam("project", required = false) project: String?
    ): ResponseEntity<JiraIssuesResponse> =
        ResponseEntity.ok(jiraService.getDoneIssues(project, quarter))

    /** 진행 중인 이슈 */
    @GetMapping("/jira/issues/in-progress")
    fun getInProgressIssues(
        @RequestParam("project", required = false) project: String?
    ): ResponseEntity<JiraIssuesResponse> =
        ResponseEntity.ok(jiraService.getInProgressIssues(project))

    /** 스프린트 이슈 */
    @GetMapping("/jira/issues/sprint")
    fun getSprintIssues(
        @RequestParam("name") sprintName: String
    ): ResponseEntity<JiraIssuesResponse> =
        ResponseEntity.ok(jiraService.getSprintIssues(sprintName))

    // ============================================================
    // 회고 데이터
    // ============================================================

    /**
     * GET /api/jira/retrospective?quarter=Q1&project=PROJ&spaceKey=SPACE
     * API 토큰 소유자(currentUser()) 기준 회고 데이터
     */
    @GetMapping("/jira/retrospective")
    fun getRetrospective(
        @RequestParam("quarter") quarter: String,
        @RequestParam("project", required = false) project: String?,
        @RequestParam("spaceKey", required = false) spaceKey: String?
    ): ResponseEntity<RetrospectiveJiraResponse> =
        ResponseEntity.ok(jiraService.getRetrospectiveData(quarter, project, spaceKey))

    /**
     * POST /api/jira/retrospective
     * 이메일 기반 회고 생성 - 클라이언트에서 email + quarter만 넘기면 됨
     *
     * Request Body:
     * {
     *   "email": "user@company.com",
     *   "quarter": "Q1",
     *   "projectKey": "PROJ",   // 선택
     *   "spaceKey": "SPACE"     // 선택 (Confluence)
     * }
     */
    @PostMapping("/jira/retrospective")
    fun generateRetrospective(
        @RequestBody request: JiraRetrospectiveRequest
    ): ResponseEntity<RetrospectiveJiraResponse> =
        ResponseEntity.ok(jiraService.generateRetrospectiveByEmail(request))

    // ============================================================
    // 프로젝트 / Confluence
    // ============================================================

    @GetMapping("/jira/projects")
    fun getProjects(): ResponseEntity<List<JiraProjectRaw>> =
        ResponseEntity.ok(jiraService.getProjects())

    @GetMapping("/confluence/pages")
    fun getConfluencePages(
        @RequestParam("spaceKey") spaceKey: String,
        @RequestParam("quarter", required = false) quarter: String?,
        @RequestParam("limit", defaultValue = "25") limit: Int
    ): ResponseEntity<ConfluencePagesResponse> =
        ResponseEntity.ok(jiraService.getConfluencePages(spaceKey, limit, quarter))
}
