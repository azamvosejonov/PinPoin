package com.pinpoint.app.domain.model

import java.time.LocalDateTime

data class Restaurant(
    val id: Int,
    val name: String,
    val address: String,
    val phone: String?,
    val logoUrl: String?,
    val ownerId: Int,
    val createdAt: LocalDateTime
)
