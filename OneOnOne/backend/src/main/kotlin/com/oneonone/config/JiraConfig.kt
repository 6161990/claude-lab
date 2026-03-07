package com.oneonone.config

import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.web.client.RestClient
import java.util.Base64

@Configuration
@EnableConfigurationProperties(JiraProperties::class)
class JiraConfig(private val jiraProperties: JiraProperties) {

    fun basicAuthHeader(): String {
        val credentials = "${jiraProperties.email}:${jiraProperties.apiToken}"
        return "Basic " + Base64.getEncoder().encodeToString(credentials.toByteArray())
    }

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
