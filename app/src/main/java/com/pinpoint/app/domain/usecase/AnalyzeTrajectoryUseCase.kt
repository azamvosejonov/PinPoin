package com.pinpoint.app.domain.usecase

import com.pinpoint.app.domain.model.TransportMode
import com.pinpoint.app.domain.model.Trajectory
import javax.inject.Inject

class AnalyzeTrajectoryUseCase @Inject constructor() {

    fun detectStopAndEntrance(trajectory: Trajectory): TrajectoryAnalysisResult {
        val points = trajectory.points
        if (points.isEmpty()) {
            return TrajectoryAnalysisResult(null, null)
        }

        val sorted = points.sortedBy { it.timestamp }
        val stopPoint = sorted.firstOrNull { it.speed != null && it.speed < 1f }
        val entrancePoint = sorted.last()

        return TrajectoryAnalysisResult(stopPoint, entrancePoint)
    }
}

data class TrajectoryAnalysisResult(
    val stopPoint: com.pinpoint.app.domain.model.LocationPoint?,
    val entrancePoint: com.pinpoint.app.domain.model.LocationPoint?
)
