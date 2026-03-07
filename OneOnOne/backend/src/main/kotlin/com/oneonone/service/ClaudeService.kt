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
    fun generateAnalysis(context: ProjectContext, response: AnalyzeResponse, customPrompt: String? = null): String? {
        if (apiKey.isBlank()) {
            log.info("ANTHROPIC_API_KEY 미설정 — AI 분석 생략")
            return null
        }

        val prompt = buildPrompt(context, response, customPrompt)
        val totalFiles = context.allFiles.size
        val userFiles = context.allFiles.count { it.touchedByUser }
        log.info("Claude 호출 — 전체 파일 ${totalFiles}개 (사용자 기여 ${userFiles}개), 프롬프트 ${prompt.length}자")

        return try {
            val request = ClaudeRequest(
                model = model,
                maxTokens = 8192,
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

    private fun buildPrompt(context: ProjectContext, data: AnalyzeResponse, customPrompt: String?): String = buildString {
        appendLine("""
당신은 소프트웨어 엔지니어링 전문가이자 시니어 테크 리드입니다.
아래에는 **프로젝트 전체 소스코드**와 **특정 개발자의 기여 내역**이 제공됩니다.
프로젝트의 전체 아키텍처와 코드 품질을 이해한 상태에서, 해당 개발자의 기여를 심층 분석해주세요.

# 분석 대상
- 개발자: ${data.userName}
- 분석 기간: ${data.startDate} ~ ${data.endDate}
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

위 소스코드와 커밋 이력을 바탕으로 **한국어**로 보고서를 작성해주세요.

규칙:
- 각 섹션은 **3줄 이내**로 핵심만 작성
- 뻔한 말("열심히 기여했습니다") 금지 — 반드시 코드나 커밋에서 근거를 찾아 구체적으로 작성
- 전체 보고서가 한눈에 읽힐 수 있도록 간결하게

---

## 1. 이번 분기 핵심 기여
이 개발자가 담당한 기능/영역과 가장 임팩트 있었던 작업 1~2개만 짧게.

## 2. 이력서 한 줄 성과
이력서 bullet point 형식으로 3개 이내. 수치나 기술 키워드 포함.

## 3. 업무 & 코드 작성 성향 분석 ← 가장 중요
★ 파일과 커밋 패턴을 기반으로 이 개발자의 성향을 분석:
- 어떤 방식으로 문제를 접근하는가? (큰 그림 먼저 vs 디테일 우선)
- 코드 스타일 성향은? (방어적 코딩 vs 간결함 추구, 추상화 수준 등)
- 커밋 단위와 메시지로 보이는 작업 습관 (잘게 나누는 편인가? 몰아서 하는 편인가?)
- 어떤 유형의 작업에서 강점을 보이는가? (기능 구현, 리팩토링, 인프라 등)
- 한 문장으로 이 개발자의 개발 성향을 정의한다면?

## 4. 코드 개선 포인트
한 줄로만 — 가장 시급한 개선 포인트와 해당 파일명.

## 5. 성장 피드백
지금 당장 도전할 수 있는 구체적인 다음 스텝 1가지.
        """.trimIndent())

        if (!customPrompt.isNullOrBlank()) {
            appendLine("\n\n# 추가 분석 요청\n")
            appendLine(customPrompt)
        }
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
