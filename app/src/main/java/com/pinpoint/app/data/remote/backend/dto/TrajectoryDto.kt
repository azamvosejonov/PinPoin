package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class TrajectoryPointDto(
    val latitude: Double,
    val longitude: Double,
    val timestamp: Long,
    val speed: Float?,
    val bearing: Float?
)

data class TrajectoryCreateRequest(
    @SerializedName("courier_id") val courierId: String,
    @SerializedName("delivered_at") val deliveredAt: Long?,
    val points: List<TrajectoryPointDto>
)

data class SyncResponseDto(
    val status: String
)

data class DomofonValidationRequestDto(
    val code: String,
    val success: Boolean
)
