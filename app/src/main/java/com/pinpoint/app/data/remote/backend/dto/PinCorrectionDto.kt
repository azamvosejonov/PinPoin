package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class PinCorrectionRequestDto(
    @SerializedName("order_id") val orderId: Int,
    @SerializedName("text_address") val textAddress: String,
    @SerializedName("gps_latitude") val gpsLatitude: Double,
    @SerializedName("gps_longitude") val gpsLongitude: Double
)

data class PinCorrectionResponseDto(
    @SerializedName("original_latitude") val originalLatitude: Double,
    @SerializedName("original_longitude") val originalLongitude: Double,
    @SerializedName("corrected_latitude") val correctedLatitude: Double,
    @SerializedName("corrected_longitude") val correctedLongitude: Double,
    @SerializedName("correction_distance_meters") val correctionDistanceMeters: Double,
    @SerializedName("source") val source: String,
    @SerializedName("confidence") val confidence: Double
)
