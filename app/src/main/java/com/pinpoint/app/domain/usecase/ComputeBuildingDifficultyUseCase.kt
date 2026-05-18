package com.pinpoint.app.domain.usecase

import com.pinpoint.app.domain.model.Building
import javax.inject.Inject

class ComputeBuildingDifficultyUseCase @Inject constructor() {

    fun compute(building: Building): Int {
        return when (building.buildingType) {
            com.pinpoint.app.domain.model.BuildingType.HRUSHCHEV -> {
                val floors = estimateFloors(building)
                (floors * 15 / 60).coerceIn(1, 5)
            }
            com.pinpoint.app.domain.model.BuildingType.NEW_TOWER -> {
                var score = 2
                if (building.requiresChip) score += 2
                if (building.hasLift) score += 1 else score += 2
                score.coerceIn(1, 5)
            }
            com.pinpoint.app.domain.model.BuildingType.OTHER -> 2
        }
    }

    private fun estimateFloors(building: Building): Int {
        return when {
            building.address.contains("qavat", ignoreCase = true) -> 5
            else -> 9
        }
    }
}
