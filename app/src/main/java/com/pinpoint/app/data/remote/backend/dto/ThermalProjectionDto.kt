package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class ThermalProjectionRequestDto(
    @SerializedName("initial_temperature") val initialTemperature: Double,
    @SerializedName("ambient_temperature") val ambientTemperature: Double,
    @SerializedName("insulation_factor") val insulationFactor: Double,
    @SerializedName("total_minutes") val totalMinutes: Int
)

data class ThermalProjectionResponseDto(
    @SerializedName("current_temperature") val currentTemperature: Double,
    @SerializedName("predicted_temperature") val predictedTemperature: Double,
    @SerializedName("eta_minutes") val etaMinutes: Int,
    @SerializedName("risk_level") val riskLevel: String
)
