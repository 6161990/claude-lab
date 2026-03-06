package com.oneonone.controller

import com.oneonone.dto.AnalysisResponse
import com.oneonone.repository.AnalysisResultRepository
import com.oneonone.service.GitAnalysisService
import org.springframework.http.MediaType
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import org.springframework.web.multipart.MultipartFile

@RestController
@RequestMapping("/api")
class AnalysisController(
    private val gitAnalysisService: GitAnalysisService,
    private val analysisResultRepository: AnalysisResultRepository
) {

    /**
     * POST /api/analyze
     * ZIP 파일 업로드 후 Git 분석 수행 → DB 저장 → 결과 반환
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
        if (repositories.isEmpty() || userName.isBlank()) {
            return ResponseEntity.badRequest().build()
        }

        val result = gitAnalysisService.analyzeRepositories(
            zipFiles = repositories,
            userName = userName,
            quarter = quarter
        )

        return ResponseEntity.ok(result.toResponse())
    }

    /**
     * GET /api/analyze/{id}
     * 저장된 분석 결과 조회 (결과 페이지에서 사용)
     */
    @GetMapping("/analyze/{id}")
    fun getAnalysisResult(@PathVariable id: Long): ResponseEntity<AnalysisResponse> {
        val result = analysisResultRepository.findById(id)
            .orElse(null) ?: return ResponseEntity.notFound().build()

        return ResponseEntity.ok(result.toResponse())
    }

    /**
     * GET /api/health
     */
    @GetMapping("/health")
    fun health(): ResponseEntity<Map<String, String>> =
        ResponseEntity.ok(mapOf("status" to "OK"))
}

// AnalysisResult → AnalysisResponse 변환
private fun com.oneonone.domain.AnalysisResult.toResponse() = AnalysisResponse(
    id = id!!,
    userName = userName,
    quarter = quarter,
    totalCommits = totalCommits,
    totalFiles = totalFiles,
    linesAdded = linesAdded,
    linesDeleted = linesDeleted,
    commitsByDate = commitsByDate
)
