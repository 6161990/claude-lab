package com.oneonone.config

import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.web.client.RestClient
import java.util.Base64

/**
 * Jira RestClient 빈 설정
 * JiraProperties가 완전히 바인딩된 후 RestClient를 생성하기 위해 분리
 */
@Configuration
@EnableConfigurationProperties(JiraProperties::class)
class JiraConfig(private val jiraProperties: JiraProperties) {

    /**
     * Jira API Basic 인증 헤더 (Base64(email:apiToken))
     */
    fun basicAuthHeader(): String {
        val credentials = "${jiraProperties.email}:${jiraProperties.apiToken}"
        return "Basic " + Base64.getEncoder().encodeToString(credentials.toByteArray())
    }

    /**
     * Jira REST API용 RestClient 빈
     * 프로퍼티 바인딩 완료 후 생성되므로 baseUrl, 인증 헤더가 올바르게 설정됨
     */
    @Bean("jiraRestClient")
    fun jiraRestClient(): RestClient {
        val baseUrl = jiraProperties.baseUrl.ifBlank { "https://placeholder.atlassian.net" }
        return RestClient.builder()
            .baseUrl(baseUrl)
            .defaultHeader("Authorization", basicAuthHeader())
            .defaultHeader("Accept", "application/json")
            .defaultHeader("Content-Type", "application/json")
            .build()
    }
}
