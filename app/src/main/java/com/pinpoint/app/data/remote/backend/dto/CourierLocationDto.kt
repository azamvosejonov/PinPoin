package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class CourierLocationDto(
    @SerializedName("courier_id") val courierId: Int,
    @SerializedName("latitude") val latitude: Double,
    @SerializedName("longitude") val longitude: Double,
    @SerializedName("updated_at") val updatedAt: String
)

data class CourierLocationUpdateDto(
    @SerializedName("latitude") val latitude: Double,
    @SerializedName("longitude") val longitude: Double
)
