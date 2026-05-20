package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class AuthRegisterDto(
    @SerializedName("email") val email: String,
    @SerializedName("password") val password: String,
    @SerializedName("full_name") val fullName: String?,
    @SerializedName("phone") val phone: String?,
    @SerializedName("role") val role: String?
)

data class AuthLoginDto(
    @SerializedName("email") val email: String,
    @SerializedName("password") val password: String
)

data class TokenPairDto(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("token_type") val tokenType: String
)

data class UserDto(
    @SerializedName("id") val id: Int,
    @SerializedName("email") val email: String,
    @SerializedName("full_name") val fullName: String?,
    @SerializedName("phone") val phone: String?,
    @SerializedName("role") val role: String,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("created_at") val createdAt: String
)
