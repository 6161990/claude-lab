package com.oneonone.config

import org.springframework.boot.context.properties.ConfigurationProperties

/**
 * Jira Cloud 연동 프로퍼티
 * @ConfigurationProperties와 @Configuration을 분리하여 바인딩 타이밍 문제 방지
 *
 * 환경변수:
 * - JIRA_BASE_URL : Jira 도메인 (예: https://your-company.atlassian.net)
 * - JIRA_EMAIL    : Atlassian 계정 이메일
 * - JIRA_API_TOKEN: Jira API 토큰
 * - JIRA_ENABLED  : 연동 활성화 여부
 */
@ConfigurationProperties(prefix = "jira")
data class JiraProperties(
    val baseUrl: String = "",
    val email: String = "",
    val apiToken: String = "",
    val enabled: Boolean = false
)
