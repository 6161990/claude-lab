package com.oneonone.config

import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.web.client.RestClient

@Configuration
class ClaudeConfig {

    @Value("\${anthropic.api-key:}")
    private lateinit var apiKey: String

    @Bean("claudeRestClient")
    fun claudeRestClient(): RestClient =
        RestClient.builder()
            .baseUrl("https://api.anthropic.com")
            .defaultHeader("x-api-key", apiKey)
            .defaultHeader("anthropic-version", "2023-06-01")
            .defaultHeader("Content-Type", "application/json")
            .build()
}
