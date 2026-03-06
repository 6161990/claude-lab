package com.oneonone.domain

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "analysis_results")
data class AnalysisResult(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(nullable = false)
    val userName: String,

    @Column(nullable = false, length = 10)
    val quarter: String,

    @Column(nullable = false)
    var totalCommits: Int = 0,

    @Column(nullable = false)
    var totalFiles: Int = 0,

    @Column(nullable = false)
    var linesAdded: Int = 0,

    @Column(nullable = false)
    var linesDeleted: Int = 0,

    // H2는 JSON 타입 미지원이므로 TEXT로 저장하고 수동 변환
    @Column(columnDefinition = "TEXT")
    var commitsByDateJson: String = "{}",

    @OneToMany(mappedBy = "analysisResult", cascade = [CascadeType.ALL], orphanRemoval = true, fetch = FetchType.LAZY)
    val commits: MutableList<CommitInfo> = mutableListOf(),

    @Column(nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    // JSON 문자열을 Map으로 변환
    @get:Transient
    var commitsByDate: Map<String, Int>
        get() = parseJsonToMap(commitsByDateJson)
        set(value) {
            commitsByDateJson = mapToJson(value)
        }

    private fun parseJsonToMap(json: String): Map<String, Int> {
        if (json == "{}") return emptyMap()
        return try {
            json.trim('{', '}')
                .split(",")
                .filter { it.isNotBlank() }
                .associate {
                    val (key, value) = it.split(":")
                    key.trim('"', ' ') to value.trim().toInt()
                }
        } catch (e: Exception) {
            emptyMap()
        }
    }

    private fun mapToJson(map: Map<String, Int>): String {
        if (map.isEmpty()) return "{}"
        return map.entries.joinToString(",", "{", "}") { (k, v) -> "\"$k\":$v" }
    }
}
