package com.oneonone.service

import com.oneonone.domain.AnalysisResult
import org.springframework.stereotype.Service
import java.time.format.DateTimeFormatter

@Service
class StatisticsService {

    /**
     * 분석 결과에서 통계를 계산합니다.
     * @param analysisResult 분석 결과 엔티티
     */
    fun calculateStatistics(analysisResult: AnalysisResult) {
        // 총 통계 계산
        analysisResult.totalCommits = analysisResult.commits.size
        analysisResult.totalFiles = analysisResult.commits.sumOf { it.filesChanged }
        analysisResult.linesAdded = analysisResult.commits.sumOf { it.insertions }
        analysisResult.linesDeleted = analysisResult.commits.sumOf { it.deletions }

        // 날짜별 커밋 수 집계 (차트용)
        val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd")
        val commitsByDate = analysisResult.commits
            .groupBy { it.commitDate.format(formatter) }
            .mapValues { it.value.size }
            .toSortedMap()

        analysisResult.commitsByDate = commitsByDate
    }
}
