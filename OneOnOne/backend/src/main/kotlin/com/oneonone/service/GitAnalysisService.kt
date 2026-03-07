package com.oneonone.service

import com.oneonone.dto.GitSummary
import org.eclipse.jgit.api.Git
import org.eclipse.jgit.diff.DiffFormatter
import org.eclipse.jgit.lib.ObjectReader
import org.eclipse.jgit.revwalk.RevCommit
import org.eclipse.jgit.revwalk.RevWalk
import org.eclipse.jgit.treewalk.CanonicalTreeParser
import org.eclipse.jgit.util.io.DisabledOutputStream
import org.springframework.stereotype.Service
import org.springframework.web.multipart.MultipartFile
import java.nio.file.Files
import java.nio.file.Path
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter

@Service
class GitAnalysisService(
    private val fileProcessingService: FileProcessingService
) {

    /**
     * 여러 ZIP 파일로부터 Git 저장소를 분석하여 GitSummary를 즉시 반환합니다.
     * DB 저장 없음.
     */
    fun analyze(
        zipFiles: Array<MultipartFile>,
        userName: String,
        quarter: String
    ): GitSummary {

        val tempDir = Files.createTempDirectory("oneonone-analysis")
        val commitInfos = mutableListOf<CommitData>()

        try {
            zipFiles.forEach { zipFile ->
                try {
                    val extractedDir = fileProcessingService.extractZipFile(zipFile, tempDir)
                    collectCommits(extractedDir, userName, quarter, commitInfos)
                } catch (e: Exception) {
                    println("ZIP 파일 처리 중 오류: ${zipFile.originalFilename}, ${e.message}")
                }
            }
        } finally {
            fileProcessingService.cleanupTempDirectory(tempDir)
        }

        // 통계 계산
        val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd")
        val commitsByDate = commitInfos
            .groupBy { it.date.format(formatter) }
            .mapValues { it.value.size }
            .toSortedMap()

        return GitSummary(
            totalCommits = commitInfos.size,
            totalFiles = commitInfos.sumOf { it.filesChanged },
            linesAdded = commitInfos.sumOf { it.insertions },
            linesDeleted = commitInfos.sumOf { it.deletions },
            commitsByDate = commitsByDate
        )
    }

    /**
     * 단일 저장소에서 커밋 데이터를 수집합니다.
     */
    private fun collectCommits(
        repoDir: Path,
        userName: String,
        quarter: String,
        result: MutableList<CommitData>
    ) {
        val gitDir = findGitDirectory(repoDir) ?: return

        Git.open(gitDir.toFile()).use { git ->
            val (startDate, endDate) = getQuarterDateRange(quarter)
            val commits = git.log().call()

            for (commit in commits) {
                val commitDate = LocalDateTime.ofInstant(
                    commit.authorIdent.`when`.toInstant(),
                    ZoneId.systemDefault()
                )

                if (commitDate.isBefore(startDate) || commitDate.isAfter(endDate)) continue
                if (!matchesUser(commit, userName)) continue

                val diffStats = analyzeDiff(git, commit)
                result.add(
                    CommitData(
                        date = commitDate,
                        filesChanged = diffStats.filesChanged,
                        insertions = diffStats.insertions,
                        deletions = diffStats.deletions
                    )
                )
            }
        }
    }

    private fun analyzeDiff(git: Git, commit: RevCommit): DiffStats {
        val repository = git.repository

        if (commit.parentCount == 0) return DiffStats(0, 0, 0)

        return try {
            val parent = commit.getParent(0)
            val reader: ObjectReader = repository.newObjectReader()

            val oldTreeIter = CanonicalTreeParser().apply {
                reset(reader, RevWalk(repository).parseCommit(parent.id).tree)
            }
            val newTreeIter = CanonicalTreeParser().apply {
                reset(reader, commit.tree)
            }

            val diffs = git.diff()
                .setOldTree(oldTreeIter)
                .setNewTree(newTreeIter)
                .call()

            val filesChanged = diffs.size
            var insertions = 0
            var deletions = 0

            val formatter = DiffFormatter(DisabledOutputStream.INSTANCE).apply {
                setRepository(repository)
            }

            for (diff in diffs) {
                val fileHeader = formatter.toFileHeader(diff)
                fileHeader.toEditList().forEach { edit ->
                    insertions += edit.endB - edit.beginB
                    deletions += edit.endA - edit.beginA
                }
            }

            DiffStats(filesChanged, insertions, deletions)
        } catch (e: Exception) {
            println("Diff 분석 중 오류: ${e.message}")
            DiffStats(0, 0, 0)
        }
    }

    private fun findGitDirectory(dir: Path): Path? {
        val gitDir = dir.resolve(".git")
        if (Files.exists(gitDir) && Files.isDirectory(gitDir)) return gitDir

        Files.walk(dir, 2).use { stream ->
            return stream
                .filter { Files.isDirectory(it) && it.fileName.toString() == ".git" }
                .findFirst()
                .orElse(null)
        }
    }

    private fun matchesUser(commit: RevCommit, userName: String): Boolean {
        val authorName = commit.authorIdent.name
        val authorEmail = commit.authorIdent.emailAddress
        return authorName.contains(userName, ignoreCase = true) ||
                authorEmail.contains(userName, ignoreCase = true)
    }

    private fun getQuarterDateRange(quarter: String): Pair<LocalDateTime, LocalDateTime> {
        val year = LocalDateTime.now().year
        return when (quarter.uppercase()) {
            "Q1" -> LocalDateTime.of(year, 1, 1, 0, 0) to LocalDateTime.of(year, 3, 31, 23, 59)
            "Q2" -> LocalDateTime.of(year, 4, 1, 0, 0) to LocalDateTime.of(year, 6, 30, 23, 59)
            "Q3" -> LocalDateTime.of(year, 7, 1, 0, 0) to LocalDateTime.of(year, 9, 30, 23, 59)
            "Q4" -> LocalDateTime.of(year, 10, 1, 0, 0) to LocalDateTime.of(year, 12, 31, 23, 59)
            else -> LocalDateTime.of(year, 1, 1, 0, 0) to LocalDateTime.now()
        }
    }

    private data class CommitData(
        val date: LocalDateTime,
        val filesChanged: Int,
        val insertions: Int,
        val deletions: Int
    )

    private data class DiffStats(
        val filesChanged: Int,
        val insertions: Int,
        val deletions: Int
    )
}
