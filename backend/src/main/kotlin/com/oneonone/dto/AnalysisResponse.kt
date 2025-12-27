package com.oneonone.dto

data class AnalysisResponse(
    val id: Long,
    val totalCommits: Int,
    val totalFiles: Int,
    val linesAdded: Int,
    val linesDeleted: Int,
    val commitsByDate: Map<String, Int>
)
