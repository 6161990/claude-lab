package com.oneonone.controller

import com.oneonone.dto.AnalyzeResponse
import org.slf4j.LoggerFactory
import com.oneonone.dto.JiraRetrospectiveRequest
import com.oneonone.service.ClaudeService
import com.oneonone.service.GitAnalysisService
import com.oneonone.service.JiraService
import org.springframework.beans.factory.annotation.Value
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
    private val jiraService: JiraService,
    private val claudeService: ClaudeService,
    @Value("\${upload.max-zip-size-mb:300}") private val maxZipSizeMb: Long,
    @Value("\${upload.max-zip-count:5}") private val maxZipCount: Int
) {

    private val logger = LoggerFactory.getLogger(OneOnOneController::class.java)

    @PostMapping("/analyze", consumes = [MULTIPART_FORM_DATA_VALUE])
    fun analyze(
        @RequestParam repositories: Array<MultipartFile>,
        @RequestParam userName: String,
        @RequestParam startDate: String,
        @RequestParam endDate: String,
        @RequestParam(required = false) jiraEmail: String?,
        @RequestParam(required = false) customPrompt: String?
    ): ResponseEntity<*> {
        val fileNames = repositories.joinToString(", ") { it.originalFilename ?: "unknown" }
        logger.info("[분석 요청] user={} | files={} | period={} ~ {}", userName, fileNames, startDate, endDate)

        // ── 검증 ──
        val validationError = validate(repositories)
        if (validationError != null) {
            return ResponseEntity.badRequest().body(mapOf("error" to validationError))
        }

        // ── 전체 프로젝트 컨텍스트 추출 ──
        val projectContext = gitAnalysisService.extractProjectContext(
            repositories, userName, startDate, endDate
        )

        // ── 기여자 커밋 없으면 조기 반환 ──
        if (projectContext.userCommits.isEmpty()) {
            return ResponseEntity.ok(
                AnalyzeResponse(
                    userName = userName,
                    startDate = startDate,
                    endDate = endDate,
                    analysis = "'${userName}'을(를) 커밋 이력에서 찾을 수 없습니다.",
                    jira = null
                )
            )
        }

        // ── Jira + Confluence 조회 (선택) ──
        val jira = jiraEmail?.let {
            jiraService.generateRetrospectiveByEmail(
                JiraRetrospectiveRequest(email = it, startDate = startDate, endDate = endDate)
            )
        }

        val partialResponse = AnalyzeResponse(
            userName = userName,
            startDate = startDate,
            endDate = endDate,
            analysis = null,
            jira = jira
        )

        // ── Claude 분석 ──
        val analysis = claudeService.generateAnalysis(projectContext, partialResponse, customPrompt)

        return ResponseEntity.ok(partialResponse.copy(analysis = analysis))
    }

    @GetMapping("/health")
    fun health(): ResponseEntity<Map<String, String>> =
        ResponseEntity.ok(mapOf("status" to "OK"))

    // ── 검증 로직 ──

    private fun validate(repositories: Array<MultipartFile>): String? {
        if (repositories.isEmpty()) return "ZIP 파일을 1개 이상 업로드해주세요."

        if (repositories.size > maxZipCount) {
            return "ZIP 파일은 최대 ${maxZipCount}개까지 업로드할 수 있습니다. (현재 ${repositories.size}개)"
        }

        val maxBytes = maxZipSizeMb * 1024 * 1024
        for (file in repositories) {
            if (!file.originalFilename.orEmpty().endsWith(".zip", ignoreCase = true)) {
                return "'${file.originalFilename}' 은(는) ZIP 파일이 아닙니다."
            }
            if (file.size > maxBytes) {
                val sizeMb = file.size / 1024 / 1024
                return "'${file.originalFilename}' 의 크기(${sizeMb}MB)가 제한(${maxZipSizeMb}MB)을 초과합니다.\n" +
                        "GitHub 저장소 1개에 해당하는 ZIP 파일을 업로드해주세요."
            }
        }
        return null
    }
}
