package com.oneonone.service

import com.oneonone.dto.CommitSummary
import com.oneonone.dto.ProjectContext
import com.oneonone.dto.ProjectFile
import org.eclipse.jgit.api.Git
import org.eclipse.jgit.revwalk.RevCommit
import org.eclipse.jgit.revwalk.RevWalk
import org.eclipse.jgit.treewalk.CanonicalTreeParser
import org.springframework.stereotype.Service
import org.springframework.web.multipart.MultipartFile
import java.nio.file.Files
import java.nio.file.Path
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import kotlin.io.path.extension
import kotlin.io.path.relativeTo

@Service
class GitAnalysisService(
    private val fileProcessingService: FileProcessingService
) {
    companion object {
        // 분석 대상 소스 파일 확장자
        private val CODE_EXTENSIONS = setOf(
            "kt", "java", "py", "ts", "tsx", "js", "jsx",
            "go", "rs", "rb", "cpp", "c", "h", "cs", "scala",
            "sql", "sh", "yaml", "yml", "toml", "gradle", "kts",
            "html", "css", "scss", "xml", "json", "md", "properties", "env"
        )

        // 제외할 디렉토리
        private val EXCLUDED_DIRS = setOf(
            "node_modules", ".git", "build", "dist", "out", ".gradle",
            "__pycache__", ".idea", ".vscode", "target", ".next",
            "coverage", ".cache", "vendor"
        )

        // Claude에 전달할 전체 소스 크기 한도 (약 120K 토큰)
        private const val TOTAL_BUDGET_CHARS = 150_000
        // 단일 파일 최대 크기
        private const val MAX_FILE_CHARS = 20_000
    }

    /**
     * ZIP에서 전체 프로젝트 소스를 추출하고, 지정 기간 동안 해당 사용자의 커밋을 수집합니다.
     * Claude가 프로젝트 전체 맥락을 이해한 뒤 기여 분석을 할 수 있도록 구성합니다.
     */
    fun extractProjectContext(
        zipFiles: Array<MultipartFile>,
        userName: String,
        startDate: String,
        endDate: String
    ): ProjectContext {
        val start = LocalDate.parse(startDate).atStartOfDay()
        val end = LocalDate.parse(endDate).atTime(23, 59, 59)
        val tempDir = Files.createTempDirectory("oneonone-analysis")

        val userCommits = mutableListOf<CommitSummary>()
        val userChangedFiles = mutableSetOf<String>()
        val allSourceFiles = mutableListOf<Pair<String, String>>() // path → content

        try {
            zipFiles.forEach { zipFile ->
                try {
                    val repoDir = fileProcessingService.extractZipFile(zipFile, tempDir)

                    // 1. 전체 소스 파일 수집
                    collectSourceFiles(repoDir, allSourceFiles)

                    // 2. 사용자 커밋 수집
                    collectUserCommits(repoDir, userName, start, end, userCommits, userChangedFiles)

                } catch (e: Exception) {
                    println("ZIP 처리 오류: ${zipFile.originalFilename}, ${e.message}")
                }
            }
        } finally {
            fileProcessingService.cleanupTempDirectory(tempDir)
        }

        // 사용자가 건드린 파일 우선, 나머지는 예산 내에서 포함
        val projectFiles = prioritizeAndTrim(allSourceFiles, userChangedFiles)
        userCommits.sortBy { it.date }

        return ProjectContext(
            allFiles = projectFiles,
            userCommits = userCommits,
            userChangedFiles = userChangedFiles
        )
    }

    /**
     * 코드 파일만 재귀 수집. 제외 디렉토리와 바이너리 파일 건너뜀.
     */
    private fun collectSourceFiles(repoDir: Path, result: MutableList<Pair<String, String>>) {
        Files.walk(repoDir).use { stream ->
            stream
                .filter { path -> Files.isRegularFile(path) }
                .filter { path ->
                    // 제외 디렉토리 필터
                    path.none { part -> EXCLUDED_DIRS.contains(part.fileName?.toString()) }
                }
                .filter { path -> CODE_EXTENSIONS.contains(path.extension.lowercase()) }
                .forEach { path ->
                    try {
                        val content = Files.readString(path, Charsets.UTF_8)
                        val relativePath = path.relativeTo(repoDir).toString()
                        result.add(relativePath to content)
                    } catch (_: Exception) {
                        // 바이너리 파일이나 읽기 실패는 무시
                    }
                }
        }
    }

    /**
     * 지정 기간 내 사용자 커밋과 변경 파일 목록 수집.
     */
    private fun collectUserCommits(
        repoDir: Path,
        userName: String,
        start: LocalDateTime,
        end: LocalDateTime,
        commits: MutableList<CommitSummary>,
        changedFiles: MutableSet<String>
    ) {
        val gitDir = findGitDirectory(repoDir) ?: return
        val dateFmt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")

        Git.open(gitDir.toFile()).use { git ->
            for (commit in git.log().call()) {
                val commitDate = LocalDateTime.ofInstant(
                    commit.authorIdent.`when`.toInstant(),
                    ZoneId.systemDefault()
                )
                if (commitDate.isBefore(start) || commitDate.isAfter(end)) continue
                if (!matchesUser(commit, userName)) continue

                val files = getChangedFilePaths(git, commit)
                changedFiles.addAll(files)

                commits.add(
                    CommitSummary(
                        date = commitDate.format(dateFmt),
                        message = commit.fullMessage.trim(),
                        changedFiles = files
                    )
                )
            }
        }
    }

    /**
     * 커밋에서 변경된 파일 경로 목록 반환.
     */
    private fun getChangedFilePaths(git: Git, commit: RevCommit): List<String> {
        if (commit.parentCount == 0) return emptyList()

        return try {
            val repo = git.repository
            val reader = repo.newObjectReader()
            val oldTree = CanonicalTreeParser().apply {
                reset(reader, RevWalk(repo).parseCommit(commit.getParent(0).id).tree)
            }
            val newTree = CanonicalTreeParser().apply { reset(reader, commit.tree) }

            git.diff().setOldTree(oldTree).setNewTree(newTree).call()
                .map { it.newPath }
        } catch (e: Exception) {
            emptyList()
        }
    }

    /**
     * 사용자 기여 파일을 우선 포함하고, 예산 범위 내에서 나머지 파일 추가.
     * 단일 파일은 MAX_FILE_CHARS로 잘라 토큰 폭발 방지.
     */
    private fun prioritizeAndTrim(
        allFiles: List<Pair<String, String>>,
        userChangedFiles: Set<String>
    ): List<ProjectFile> {
        val result = mutableListOf<ProjectFile>()
        var usedChars = 0

        // 1순위: 사용자가 수정한 파일 (전체 포함)
        val userFiles = allFiles.filter { (path, _) ->
            userChangedFiles.any { changed -> path.endsWith(changed) || changed.endsWith(path) }
        }
        for ((path, rawContent) in userFiles) {
            val content = rawContent.take(MAX_FILE_CHARS)
            result.add(ProjectFile(path, content, touchedByUser = true))
            usedChars += content.length
        }

        // 2순위: 나머지 파일 (예산 내에서)
        val otherFiles = allFiles.filter { (path, _) ->
            userFiles.none { (up, _) -> up == path }
        }.sortedBy { it.first } // 경로 순 정렬로 일관성 유지

        for ((path, rawContent) in otherFiles) {
            if (usedChars >= TOTAL_BUDGET_CHARS) break
            val content = rawContent.take(MAX_FILE_CHARS)
            result.add(ProjectFile(path, content, touchedByUser = false))
            usedChars += content.length
        }

        return result
    }

    private fun findGitDirectory(dir: Path): Path? {
        val gitDir = dir.resolve(".git")
        if (Files.exists(gitDir) && Files.isDirectory(gitDir)) return gitDir
        Files.walk(dir, 2).use { stream ->
            return stream.filter { Files.isDirectory(it) && it.fileName.toString() == ".git" }
                .findFirst().orElse(null)
        }
    }

    private fun matchesUser(commit: RevCommit, userName: String): Boolean =
        commit.authorIdent.name.contains(userName, ignoreCase = true) ||
                commit.authorIdent.emailAddress.contains(userName, ignoreCase = true)
}
