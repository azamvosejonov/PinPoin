package com.pinpoint.app.domain.usecase

import com.pinpoint.app.domain.model.ThermalProjection
import com.pinpoint.app.domain.model.ThermalRiskLevel
import kotlin.math.exp
import javax.inject.Inject

class ComputeThermalProjectionUseCase @Inject constructor() {

    fun compute(
        initialTemperature: Double,
        ambientTemperature: Double,
        insulationFactor: Double,
        totalMinutes: Int
    ): ThermalProjection {
        val decayConstant = (1 - insulationFactor).coerceIn(0.1, 0.9)
        val predictedTemperature = ambientTemperature + (initialTemperature - ambientTemperature) * exp(-decayConstant * totalMinutes / 10)
        val risk = when {
            predictedTemperature >= 60 -> ThermalRiskLevel.LOW
            predictedTemperature >= 45 -> ThermalRiskLevel.MEDIUM
            else -> ThermalRiskLevel.HIGH
        }
        return ThermalProjection(
            currentTemperature = initialTemperature,
            predictedTemperature = predictedTemperature,
            etaMinutes = totalMinutes,
            riskLevel = risk
        )
    }
}
