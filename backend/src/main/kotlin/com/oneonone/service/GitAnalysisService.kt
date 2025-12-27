package com.oneonone.service

import com.oneonone.domain.AnalysisResult
import com.oneonone.domain.CommitInfo
import com.oneonone.repository.AnalysisResultRepository
import org.eclipse.jgit.api.Git
import org.eclipse.jgit.diff.DiffFormatter
import org.eclipse.jgit.lib.ObjectReader
import org.eclipse.jgit.revwalk.RevCommit
import org.eclipse.jgit.revwalk.RevWalk
import org.eclipse.jgit.treewalk.CanonicalTreeParser
import org.eclipse.jgit.util.io.DisabledOutputStream
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.multipart.MultipartFile
import java.nio.file.Files
import java.nio.file.Path
import java.time.LocalDateTime
import java.time.ZoneId

@Service
@Transactional
class GitAnalysisService(
    private val analysisResultRepository: AnalysisResultRepository,
    private val fileProcessingService: FileProcessingService,
    private val statisticsService: StatisticsService
) {

    /**
     * 여러 ZIP 파일로부터 Git 저장소를 분석합니다.
     * @param zipFiles 업로드된 ZIP 파일 배열
     * @param userName Git 사용자 이름
     * @param quarter 분석 분기
     * @return 분석 결과
     */
    fun analyzeRepositories(
        zipFiles: Array<MultipartFile>,
        userName: String,
        quarter: String
    ): AnalysisResult {

        val analysisResult = AnalysisResult(
            userName = userName,
            quarter = quarter
        )

        // 임시 디렉토리 생성
        val tempDir = Files.createTempDirectory("oneonone-analysis")

        try {
            // 각 ZIP 파일 처리
            zipFiles.forEach { zipFile ->
                try {
                    val extractedDir = fileProcessingService.extractZipFile(zipFile, tempDir)
                    analyzeRepository(extractedDir, userName, quarter, analysisResult)
                } catch (e: Exception) {
                    println("ZIP 파일 처리 중 오류: ${zipFile.originalFilename}, ${e.message}")
                }
            }

            // 통계 계산
            statisticsService.calculateStatistics(analysisResult)

            // DB 저장
            return analysisResultRepository.save(analysisResult)

        } finally {
            // 임시 파일 정리
            fileProcessingService.cleanupTempDirectory(tempDir)
        }
    }

    /**
     * 단일 저장소를 분석합니다.
     */
    private fun analyzeRepository(
        repoDir: Path,
        userName: String,
        quarter: String,
        analysisResult: AnalysisResult
    ) {
        // .git 디렉토리 찾기
        val gitDir = findGitDirectory(repoDir) ?: return

        Git.open(gitDir.toFile()).use { git ->
            // 커밋 범위 설정 (분기별)
            val (startDate, endDate) = getQuarterDateRange(quarter)

            // 모든 커밋 조회
            val commits = git.log().call()

            for (commit in commits) {
                val commitDate = LocalDateTime.ofInstant(
                    commit.authorIdent.`when`.toInstant(),
                    ZoneId.systemDefault()
                )

                // 분기 범위 체크
                if (commitDate.isBefore(startDate) || commitDate.isAfter(endDate)) {
                    continue
                }

                // 사용자 이름/이메일 매칭
                if (!matchesUser(commit, userName)) {
                    continue
                }

                // 커밋 변경 내역 분석
                val diffStats = analyzeDiff(git, commit)

                // CommitInfo 생성
                val commitInfo = CommitInfo(
                    analysisResult = analysisResult,
                    commitHash = commit.name,
                    authorName = commit.authorIdent.name,
                    authorEmail = commit.authorIdent.emailAddress,
                    commitDate = commitDate,
                    message = commit.fullMessage,
                    filesChanged = diffStats.filesChanged,
                    insertions = diffStats.insertions,
                    deletions = diffStats.deletions
                )

                analysisResult.commits.add(commitInfo)
            }
        }
    }

    /**
     * 커밋의 Diff를 분석하여 통계를 계산합니다.
     */
    private fun analyzeDiff(git: Git, commit: RevCommit): DiffStats {
        val repository = git.repository

        if (commit.parentCount == 0) {
            // 초기 커밋 - 부모 없음
            return DiffStats(0, 0, 0)
        }

        try {
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

            // 라인 수 계산
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

            return DiffStats(filesChanged, insertions, deletions)

        } catch (e: Exception) {
            println("Diff 분석 중 오류: ${e.message}")
            return DiffStats(0, 0, 0)
        }
    }

    /**
     * .git 디렉토리를 찾습니다.
     */
    private fun findGitDirectory(dir: Path): Path? {
        val gitDir = dir.resolve(".git")
        if (Files.exists(gitDir) && Files.isDirectory(gitDir)) {
            return gitDir
        }

        // 하위 디렉토리에서 찾기 (최대 2단계)
        Files.walk(dir, 2).use { stream ->
            return stream
                .filter { Files.isDirectory(it) && it.fileName.toString() == ".git" }
                .findFirst()
                .orElse(null)
        }
    }

    /**
     * 커밋 작성자가 사용자와 일치하는지 확인합니다.
     */
    private fun matchesUser(commit: RevCommit, userName: String): Boolean {
        val authorName = commit.authorIdent.name
        val authorEmail = commit.authorIdent.emailAddress

        return authorName.contains(userName, ignoreCase = true) ||
                authorEmail.contains(userName, ignoreCase = true)
    }

    /**
     * 분기별 날짜 범위를 반환합니다.
     */
    private fun getQuarterDateRange(quarter: String): Pair<LocalDateTime, LocalDateTime> {
        val year = LocalDateTime.now().year

        return when (quarter) {
            "Q1" -> Pair(
                LocalDateTime.of(year, 1, 1, 0, 0),
                LocalDateTime.of(year, 3, 31, 23, 59)
            )
            "Q2" -> Pair(
                LocalDateTime.of(year, 4, 1, 0, 0),
                LocalDateTime.of(year, 6, 30, 23, 59)
            )
            "Q3" -> Pair(
                LocalDateTime.of(year, 7, 1, 0, 0),
                LocalDateTime.of(year, 9, 30, 23, 59)
            )
            "Q4" -> Pair(
                LocalDateTime.of(year, 10, 1, 0, 0),
                LocalDateTime.of(year, 12, 31, 23, 59)
            )
            else -> Pair(
                LocalDateTime.of(year, 1, 1, 0, 0),
                LocalDateTime.now()
            )
        }
    }

    /**
     * Diff 통계 데이터 클래스
     */
    private data class DiffStats(
        val filesChanged: Int,
        val insertions: Int,
        val deletions: Int
    )
}
