package com.oneonone.dto

// POST /api/analyze 응답
data class AnalyzeResponse(
    val userName: String,
    val startDate: String,
    val endDate: String,
    val analysis: String?,                // Claude AI 분석 보고서
    val jira: RetrospectiveJiraResponse?  // jiraEmail 없으면 null
)

// Claude에 전달하기 위한 내부 프로젝트 컨텍스트 (API 응답에 포함되지 않음)
data class ProjectContext(
    val allFiles: List<ProjectFile>,         // 전체 프로젝트 소스 파일
    val userCommits: List<CommitSummary>,    // 사용자 커밋 목록
    val userChangedFiles: Set<String>        // 사용자가 수정한 파일 경로
)

data class ProjectFile(
    val path: String,
    val content: String,
    val touchedByUser: Boolean
)

data class CommitSummary(
    val date: String,
    val message: String,
    val changedFiles: List<String>
)
