package com.oneonone

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.context.properties.ConfigurationPropertiesScan
import org.springframework.boot.runApplication

@SpringBootApplication
@ConfigurationPropertiesScan
class OneOnOneApplication

fun main(args: Array<String>) {
    runApplication<OneOnOneApplication>(*args)
}
