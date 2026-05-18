package com.pinpoint.app.data.repository

import com.pinpoint.app.data.local.dao.TrajectoryDao
import com.pinpoint.app.data.mapper.toDomain
import com.pinpoint.app.data.mapper.toEntity
import com.pinpoint.app.data.remote.backend.BackendApi
import com.pinpoint.app.data.remote.backend.dto.TrajectoryCreateRequest
import com.pinpoint.app.data.remote.backend.dto.TrajectoryPointDto
import com.pinpoint.app.domain.model.Trajectory
import com.pinpoint.app.domain.repository.TrajectoryRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

class TrajectoryRepositoryImpl @Inject constructor(
    private val trajectoryDao: TrajectoryDao,
    private val backendApi: BackendApi
) : TrajectoryRepository {

    override suspend fun saveTrajectory(trajectory: Trajectory) {
        trajectoryDao.insertTrajectory(trajectory.toEntity())
        val request = TrajectoryCreateRequest(
            courierId = trajectory.courierId,
            deliveredAt = trajectory.deliveredAt,
            points = trajectory.points.map {
                TrajectoryPointDto(
                    latitude = it.latitude,
                    longitude = it.longitude,
                    timestamp = it.timestamp,
                    speed = it.speed,
                    bearing = it.bearing
                )
            }
        )
        runCatching { backendApi.submitTrajectory(trajectory.buildingExternalId, request) }
    }

    override suspend fun getRecentTrajectories(buildingExternalId: String): List<Trajectory> =
        trajectoryDao.getRecentTrajectories(buildingExternalId).map { it.toDomain() }

    override fun observeCourierTrajectories(courierId: String): Flow<List<Trajectory>> =
        trajectoryDao.observeTrajectoriesForCourier(courierId).map { list -> list.map { it.toDomain() } }
}
