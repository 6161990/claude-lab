package com.oneonone.config

import org.springframework.context.annotation.Configuration
import org.springframework.web.servlet.config.annotation.CorsRegistry
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer

/**
 * 웹 전역 설정
 * CORS는 여기서 단일 관리 (컨트롤러 @CrossOrigin 중복 사용 금지)
 */
@Configuration
class WebConfig : WebMvcConfigurer {

    override fun addCorsMappings(registry: CorsRegistry) {
        registry.addMapping("/api/**")
            .allowedOrigins(
                "http://localhost:3000",      // Next.js 개발 서버
                "http://localhost:8000",      // 레거시 프론트엔드
                "http://127.0.0.1:8000",
                "https://*.github.io"         // GitHub Pages 배포
            )
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
            .allowedHeaders("*")
            .allowCredentials(true)
            .maxAge(3600)
    }
}
