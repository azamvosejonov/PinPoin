package com.pinpoint.app.domain.usecase

import com.pinpoint.app.domain.repository.BuildingRepository
import com.pinpoint.app.domain.repository.TrajectoryRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import javax.inject.Inject

class OfflineSyncUseCase @Inject constructor(
    private val buildingRepository: BuildingRepository,
    private val trajectoryRepository: TrajectoryRepository
) {
    private val scope = CoroutineScope(Dispatchers.IO)

    fun syncBuilding(externalId: String, address: String, coordinate: com.pinpoint.app.domain.model.Coordinate) {
        scope.launch {
            buildingRepository.refreshBuilding(externalId, address, coordinate)
        }
    }

    fun recordTrajectory(trajectory: com.pinpoint.app.domain.model.Trajectory) {
        scope.launch {
            trajectoryRepository.saveTrajectory(trajectory)
        }
    }
}
