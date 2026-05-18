package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class PredictivePinRequestDto(
    @SerializedName("raw_coordinate") val rawCoordinate: CoordinateDto,
    @SerializedName("address_embedding") val addressEmbedding: List<Float>,
    @SerializedName("historical_vector") val historicalVector: List<Float>
)

data class PredictivePinResponseDto(
    @SerializedName("adjusted_coordinate") val adjustedCoordinate: CoordinateDto,
    @SerializedName("delta_lat") val deltaLat: Double,
    @SerializedName("delta_lon") val deltaLon: Double
)

data class CoordinateDto(
    val latitude: Double,
    val longitude: Double
)
