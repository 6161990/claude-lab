package com.oneonone.domain

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "commit_infos")
data class CommitInfo(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "analysis_result_id", nullable = false)
    val analysisResult: AnalysisResult,

    @Column(nullable = false, length = 40)
    val commitHash: String,

    @Column(nullable = false)
    val authorName: String,

    @Column(nullable = false)
    val authorEmail: String,

    @Column(nullable = false)
    val commitDate: LocalDateTime,

    @Column(nullable = false, columnDefinition = "TEXT")
    val message: String,

    @Column(nullable = false)
    val filesChanged: Int = 0,

    @Column(nullable = false)
    val insertions: Int = 0,

    @Column(nullable = false)
    val deletions: Int = 0
)
