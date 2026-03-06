package com.oneonone.dto

data class AnalysisResponse(
    val id: Long,
    val userName: String,
    val quarter: String,
    val totalCommits: Int,
    val totalFiles: Int,
    val linesAdded: Int,
    val linesDeleted: Int,
    val commitsByDate: Map<String, Int>
)
