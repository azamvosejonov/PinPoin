package com.pinpoint.app.domain.usecase

import com.pinpoint.app.domain.model.LocationPoint
import com.pinpoint.app.domain.model.Trajectory
import kotlin.math.pow
import kotlin.math.sqrt
import javax.inject.Inject

class IdentifyEntranceFromTrajectoriesUseCase @Inject constructor() {

    fun identifyEntrancePoint(trajectories: List<Trajectory>): LocationPoint? {
        if (trajectories.isEmpty()) return null
        val allPoints = trajectories.flatMap { it.points }
        if (allPoints.isEmpty()) return null

        val cluster = allPoints.groupBy { bucketKey(it.latitude, it.longitude) }
            .maxByOrNull { it.value.size }?.value ?: return null
        return centerOfMass(cluster)
    }

    private fun bucketKey(lat: Double, lon: Double, precision: Double = 0.0001): Pair<Int, Int> {
        val x = (lat / precision).toInt()
        val y = (lon / precision).toInt()
        return x to y
    }

    private fun centerOfMass(points: List<LocationPoint>): LocationPoint {
        val avgLat = points.map { it.latitude }.average()
        val avgLon = points.map { it.longitude }.average()
        val latestTimestamp = points.maxOf { it.timestamp }
        return LocationPoint(
            latitude = avgLat,
            longitude = avgLon,
            timestamp = latestTimestamp,
            speed = null,
            bearing = null
        )
    }
}
