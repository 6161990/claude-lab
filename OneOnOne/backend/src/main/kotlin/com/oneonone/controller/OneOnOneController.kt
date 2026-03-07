package com.oneonone.controller

import com.oneonone.dto.AnalyzeResponse
import com.oneonone.dto.JiraRetrospectiveRequest
import com.oneonone.service.GitAnalysisService
import com.oneonone.service.JiraService
import org.springframework.http.MediaType.MULTIPART_FORM_DATA_VALUE
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.multipart.MultipartFile

@RestController
@RequestMapping("/api")
class OneOnOneController(
    private val gitAnalysisService: GitAnalysisService,
    private val jiraService: JiraService
) {

    /**
     * Git 저장소 ZIP 파일들을 분석하여 즉시 반환합니다. DB 저장 없음.
     */
    @PostMapping("/analyze", consumes = [MULTIPART_FORM_DATA_VALUE])
    fun analyze(
        @RequestParam repositories: Array<MultipartFile>,
        @RequestParam userName: String,
        @RequestParam quarter: String,
        @RequestParam(required = false) jiraEmail: String?
    ): ResponseEntity<AnalyzeResponse> {
        val git = gitAnalysisService.analyze(repositories, userName, quarter)
        val jira = jiraEmail?.let {
            jiraService.generateRetrospectiveByEmail(
                JiraRetrospectiveRequest(email = it, quarter = quarter)
            )
        }
        return ResponseEntity.ok(AnalyzeResponse(userName, quarter, git, jira))
    }

    @GetMapping("/health")
    fun health(): ResponseEntity<Map<String, String>> =
        ResponseEntity.ok(mapOf("status" to "OK"))
}
