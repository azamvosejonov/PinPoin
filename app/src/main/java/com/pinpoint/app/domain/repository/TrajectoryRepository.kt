package com.pinpoint.app.domain.repository

import com.pinpoint.app.domain.model.Trajectory
import kotlinx.coroutines.flow.Flow

interface TrajectoryRepository {
    suspend fun saveTrajectory(trajectory: Trajectory)
    suspend fun getRecentTrajectories(buildingExternalId: String): List<Trajectory>
    fun observeCourierTrajectories(courierId: String): Flow<List<Trajectory>>
}
