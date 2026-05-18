package com.pinpoint.app.service

import android.location.Location
import com.pinpoint.app.domain.model.LocationPoint
import com.pinpoint.app.domain.model.Trajectory
import com.pinpoint.app.domain.repository.TrajectoryRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TrajectoryRecorder @Inject constructor(
    private val trajectoryRepository: TrajectoryRepository
) {

    private val scope = CoroutineScope(Dispatchers.IO + Job())
    private val locationFlow = MutableSharedFlow<LocationPoint>(replay = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)
    val locationUpdates = locationFlow.asSharedFlow()

    private val currentPoints = mutableListOf<LocationPoint>()

    fun recordLocation(location: Location) {
        val point = LocationPoint(
            latitude = location.latitude,
            longitude = location.longitude,
            timestamp = location.time,
            speed = location.speed,
            bearing = location.bearing
        )
        currentPoints.add(point)
        scope.launch { locationFlow.emit(point) }
    }

    fun saveTrajectory(buildingExternalId: String, courierId: String) {
        if (currentPoints.isEmpty()) return
        val trajectory = Trajectory(
            id = 0,
            buildingExternalId = buildingExternalId,
            courierId = courierId,
            deliveredAt = System.currentTimeMillis(),
            points = currentPoints.toList()
        )
        scope.launch {
            trajectoryRepository.saveTrajectory(trajectory)
        }
        currentPoints.clear()
    }
}
