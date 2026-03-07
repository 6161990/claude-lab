package com.oneonone.dto

// Git 분석 요약 (DB 저장 없이 즉시 반환)
data class GitSummary(
    val totalCommits: Int,
    val totalFiles: Int,
    val linesAdded: Int,
    val linesDeleted: Int,
    val commitsByDate: Map<String, Int>
)

// POST /api/analyze 통합 응답
data class AnalyzeResponse(
    val userName: String,
    val quarter: String,
    val git: GitSummary,
    val jira: RetrospectiveJiraResponse?  // jiraEmail 없으면 null
)
