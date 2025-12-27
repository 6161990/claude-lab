package com.oneonone.repository

import com.oneonone.domain.AnalysisResult
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface AnalysisResultRepository : JpaRepository<AnalysisResult, Long> {
    // 사용자 이름과 분기로 조회
    fun findByUserNameAndQuarter(userName: String, quarter: String): List<AnalysisResult>

    // 사용자 이름으로 조회
    fun findByUserName(userName: String): List<AnalysisResult>
}
