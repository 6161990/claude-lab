package com.oneonone.config

import org.springframework.boot.context.properties.ConfigurationProperties

@ConfigurationProperties(prefix = "jira")
data class JiraProperties(
    val baseUrl: String = "",
    val email: String = "",
    val apiToken: String = "",
    val enabled: Boolean = false
)
