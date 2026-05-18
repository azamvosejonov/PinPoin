package com.pinpoint.app.domain.usecase

import com.pinpoint.app.domain.model.Building
import com.pinpoint.app.domain.model.ThermalProjection
import javax.inject.Inject

class GenerateThermalRouteAdviceUseCase @Inject constructor(
    private val computeBuildingDifficultyUseCase: ComputeBuildingDifficultyUseCase
) {

    fun generateAdvice(building: Building, projection: ThermalProjection): ThermalRouteAdvice {
        val difficulty = computeBuildingDifficultyUseCase.compute(building)
        val extraMinutes = when (difficulty) {
            in 1..2 -> 2
            3 -> 4
            else -> 6
        }
        val totalMinutes = projection.etaMinutes + extraMinutes
        val warning = when (projection.riskLevel) {
            com.pinpoint.app.domain.model.ThermalRiskLevel.LOW -> null
            com.pinpoint.app.domain.model.ThermalRiskLevel.MEDIUM -> "Mijozga qo'ng'iroq qilib, liftni tayyorlab qo'yishni so'rang"
            com.pinpoint.app.domain.model.ThermalRiskLevel.HIGH -> "Eng qisqa yo'lni tanlang va mijozdan pastga tushishini iltimos qiling"
        }
        return ThermalRouteAdvice(
            totalEtaMinutes = totalMinutes,
            warningMessage = warning
        )
    }
}

data class ThermalRouteAdvice(
    val totalEtaMinutes: Int,
    val warningMessage: String?
)
