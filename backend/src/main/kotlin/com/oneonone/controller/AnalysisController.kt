package com.oneonone.controller

import com.oneonone.dto.AnalysisResponse
import com.oneonone.service.GitAnalysisService
import org.springframework.http.MediaType
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import org.springframework.web.multipart.MultipartFile

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = ["http://localhost:8000", "https://*.github.io"])
class AnalysisController(
    private val gitAnalysisService: GitAnalysisService
) {

    /**
     * POST /api/analyze
     *
     * ZIP 파일 형태의 Git 저장소들을 분석하여 통계를 반환합니다.
     *
     * @param repositories 업로드된 ZIP 파일들 (MultipartFile[])
     * @param userName Git 사용자 이름 또는 이메일
     * @param quarter 분석 기간 (Q1, Q2, Q3, Q4)
     * @return AnalysisResponse (commits, files, linesAdded, linesDeleted, activityData)
     */
    @PostMapping(
        "/analyze",
        consumes = [MediaType.MULTIPART_FORM_DATA_VALUE],
        produces = [MediaType.APPLICATION_JSON_VALUE]
    )
    fun analyzeRepositories(
        @RequestParam("repositories") repositories: Array<MultipartFile>,
        @RequestParam("userName") userName: String,
        @RequestParam("quarter") quarter: String
    ): ResponseEntity<AnalysisResponse> {

        // 입력 검증
        if (repositories.isEmpty()) {
            return ResponseEntity.badRequest().build()
        }

        if (userName.isBlank()) {
            return ResponseEntity.badRequest().build()
        }

        // Git 분석 수행
        val analysisResult = gitAnalysisService.analyzeRepositories(
            zipFiles = repositories,
            userName = userName,
            quarter = quarter
        )

        // 응답 생성
        val response = AnalysisResponse(
            id = analysisResult.id!!,
            totalCommits = analysisResult.totalCommits,
            totalFiles = analysisResult.totalFiles,
            linesAdded = analysisResult.linesAdded,
            linesDeleted = analysisResult.linesDeleted,
            commitsByDate = analysisResult.commitsByDate
        )

        return ResponseEntity.ok(response)
    }

    /**
     * GET /api/health
     *
     * 헬스체크 엔드포인트
     */
    @GetMapping("/health")
    fun health(): ResponseEntity<Map<String, String>> {
        return ResponseEntity.ok(mapOf("status" to "OK"))
    }
}
