package com.oneonone.service

import org.apache.commons.compress.archivers.zip.ZipArchiveInputStream
import org.springframework.stereotype.Service
import org.springframework.web.multipart.MultipartFile
import java.nio.file.Files
import java.nio.file.Path
import java.util.Comparator

@Service
class FileProcessingService {

    /**
     * ZIP 파일을 압축 해제합니다.
     * @param zipFile 업로드된 ZIP 파일
     * @param targetDir 압축 해제할 대상 디렉토리
     * @return 압축 해제된 디렉토리 경로
     */
    fun extractZipFile(zipFile: MultipartFile, targetDir: Path): Path {
        val extractDir = Files.createTempDirectory(targetDir, "repo-")

        zipFile.inputStream.use { inputStream ->
            val zipInputStream = ZipArchiveInputStream(inputStream)
            var entry = zipInputStream.nextEntry

            while (entry != null) {
                val entryFile = extractDir.resolve(entry.name)

                if (entry.isDirectory) {
                    Files.createDirectories(entryFile)
                } else {
                    // 부모 디렉토리가 없으면 생성
                    Files.createDirectories(entryFile.parent)
                    Files.copy(zipInputStream, entryFile)
                }

                entry = zipInputStream.nextEntry
            }
        }

        return extractDir
    }

    /**
     * 임시 디렉토리를 삭제합니다.
     * @param dir 삭제할 디렉토리 경로
     */
    fun cleanupTempDirectory(dir: Path) {
        if (Files.exists(dir)) {
            Files.walk(dir)
                .sorted(Comparator.reverseOrder())
                .forEach { Files.deleteIfExists(it) }
        }
    }
}
