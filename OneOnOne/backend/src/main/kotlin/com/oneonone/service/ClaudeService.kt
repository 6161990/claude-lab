package com.oneonone.service

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import com.oneonone.dto.AnalyzeResponse
import com.oneonone.dto.ProjectContext
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Qualifier
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import org.springframework.web.client.RestClient
import org.springframework.web.client.RestClientException

@Service
class ClaudeService(
    @Qualifier("claudeRestClient") private val restClient: RestClient,
    @Value("\${anthropic.api-key:}") private val apiKey: String,
    @Value("\${anthropic.model:claude-sonnet-4-6}") private val model: String
) {
    private val log = LoggerFactory.getLogger(ClaudeService::class.java)

    /**
     * 전체 프로젝트 소스 + 사용자 기여 내역 + Jira 데이터를 Claude에 전달하여
     * 프로젝트 전체 맥락을 이해한 심층 분석 보고서를 생성합니다.
     */
    fun generateAnalysis(context: ProjectContext, response: AnalyzeResponse): String? {
        if (apiKey.isBlank()) {
            log.info("ANTHROPIC_API_KEY 미설정 — AI 분석 생략")
            return null
        }

        val prompt = buildPrompt(context, response)
        val totalFiles = context.allFiles.size
        val userFiles = context.allFiles.count { it.touchedByUser }
        log.info("Claude 호출 — 전체 파일 ${totalFiles}개 (사용자 기여 ${userFiles}개), 프롬프트 ${prompt.length}자")

        return try {
            val request = ClaudeRequest(
                model = model,
                maxTokens = 4096,
                messages = listOf(ClaudeMessage(role = "user", content = prompt))
            )
            val response2 = restClient.post()
                .uri("/v1/messages")
                .body(request)
                .retrieve()
                .body(ClaudeResponse::class.java)

            response2?.content?.firstOrNull()?.text
        } catch (e: RestClientException) {
            log.error("Claude API 호출 실패: ${e.message}")
            null
        }
    }

    private fun buildPrompt(context: ProjectContext, data: AnalyzeResponse): String = buildString {
        appendLine("""
당신은 소프트웨어 엔지니어링 전문가이자 시니어 테크 리드입니다.
아래에는 **프로젝트 전체 소스코드**와 **특정 개발자의 기여 내역**이 제공됩니다.
프로젝트의 전체 아키텍처와 코드 품질을 이해한 상태에서, 해당 개발자의 기여를 심층 분석해주세요.

# 분석 대상
- 개발자: ${data.userName}
- 분석 기간: ${data.startDate} ~ ${data.endDate}
- 기간 내 커밋 수: ${context.userCommits.size}개
- 기여 파일 수: ${context.userChangedFiles.size}개
        """.trimIndent())

        // ── 전체 프로젝트 소스코드 ──
        appendLine("\n\n# 프로젝트 전체 소스코드\n")
        appendLine("※ ★ 표시는 ${data.userName}이(가) 분석 기간에 수정한 파일입니다.\n")

        for (file in context.allFiles) {
            val marker = if (file.touchedByUser) "★ " else ""
            appendLine("=== ${marker}${file.path} ===")
            appendLine(file.content)
            appendLine()
        }

        // ── 사용자 기여 내역 ──
        appendLine("\n\n# ${data.userName}의 기여 내역 (${data.startDate} ~ ${data.endDate})\n")

        if (context.userCommits.isEmpty()) {
            appendLine("해당 기간에 커밋이 없습니다.")
        } else {
            for (commit in context.userCommits) {
                appendLine("## [${commit.date}] ${commit.message.lines().first()}")
                if (commit.message.lines().size > 1) {
                    appendLine(commit.message.lines().drop(1).joinToString("\n").trim())
                }
                if (commit.changedFiles.isNotEmpty()) {
                    appendLine("변경 파일: ${commit.changedFiles.joinToString(", ")}")
                }
                appendLine()
            }
        }

        // ── Jira / Confluence ──
        val jira = data.jira
        if (jira != null) {
            appendLine("\n# Jira / Confluence 업무 데이터\n")

            appendLine("## 완료된 이슈 (${jira.totalDone}개)")
            if (jira.doneIssues.isEmpty()) {
                appendLine("없음")
            } else {
                jira.doneIssues.forEach {
                    appendLine("- [${it.key}] ${it.summary} (${it.issueType} | ${it.project})")
                }
            }

            appendLine("\n## 진행 중 이슈 (${jira.totalInProgress}개)")
            if (jira.inProgressIssues.isEmpty()) {
                appendLine("없음")
            } else {
                jira.inProgressIssues.forEach {
                    appendLine("- [${it.key}] ${it.summary} (${it.issueType} | ${it.project})")
                }
            }

            if (jira.confluencePages.isNotEmpty()) {
                appendLine("\n## Confluence 기여 페이지 (${jira.confluencePages.size}개)")
                jira.confluencePages.forEach {
                    appendLine("- ${it.title} (공간: ${it.spaceName}, 수정일: ${it.lastUpdated.take(10)})")
                }
            }
        }

        // ── 분석 요청 ──
        appendLine("""


---

# 분석 요청

위 프로젝트 전체 코드베이스를 완전히 파악한 상태에서, **${data.userName}**의 기여에 대해 다음 항목을 포함한 전문가 회고 보고서를 **한국어**로 작성해주세요.

1. **기여 요약** — 이 개발자가 프로젝트에서 어떤 역할을 했는지, 어떤 기능/영역을 담당했는지

2. **코드 품질 심층 분석** — 프로젝트 전체 맥락에서 평가:
   - 이 개발자의 코드가 전체 아키텍처에 어떻게 녹아드는가
   - 코드 스타일, 가독성, 명명 규칙
   - 설계 패턴 활용, 추상화 수준의 적절성
   - 에러 처리, 예외 상황 고려
   - 잠재적 버그나 개선이 필요한 코드 (구체적 파일명/함수명 언급)

3. **아키텍처 기여도** — 전체 시스템 설계 관점에서의 기여 평가

4. **강점** — 코드에서 드러나는 뛰어난 역량 (구체적 코드 예시 포함)

5. **개선 제안** — 구체적인 파일/함수를 지목하여 개선 방향 제시

6. **성장 로드맵** — 이 개발자에게 권장하는 다음 단계 학습/도전 과제

코드의 실제 내용을 인용하고, 전체 프로젝트 구조와 비교하여 구체적으로 분석해주세요.
""".trimIndent())
    }
}

// Claude API 내부 DTO
data class ClaudeRequest(
    val model: String,
    @JsonProperty("max_tokens") val maxTokens: Int,
    val messages: List<ClaudeMessage>
)

data class ClaudeMessage(val role: String, val content: String)

@JsonIgnoreProperties(ignoreUnknown = true)
data class ClaudeResponse(val content: List<ClaudeContent> = emptyList())

@JsonIgnoreProperties(ignoreUnknown = true)
data class ClaudeContent(val type: String = "", val text: String = "")
