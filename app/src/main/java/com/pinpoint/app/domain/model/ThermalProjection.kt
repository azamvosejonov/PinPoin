package com.pinpoint.app.domain.model

data class ThermalProjection(
    val currentTemperature: Double,
    val predictedTemperature: Double,
    val etaMinutes: Int,
    val riskLevel: ThermalRiskLevel
)
