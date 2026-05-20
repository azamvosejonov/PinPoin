package com.pinpoint.app.domain.model

import java.time.LocalDateTime

data class User(
    val id: Int,
    val email: String,
    val fullName: String?,
    val phone: String?,
    val role: UserRole,
    val isActive: Boolean,
    val createdAt: LocalDateTime
)

enum class UserRole {
    ADMIN,
    RESTAURANT_OWNER,
    RESTAURANT_OPERATOR,
    COURIER
}

data class TokenPair(
    val accessToken: String,
    val refreshToken: String,
    val tokenType: String
)
