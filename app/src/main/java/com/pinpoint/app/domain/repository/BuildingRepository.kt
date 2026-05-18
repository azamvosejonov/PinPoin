package com.pinpoint.app.domain.repository

import com.pinpoint.app.domain.model.Building
import com.pinpoint.app.domain.model.Coordinate
import kotlinx.coroutines.flow.Flow

interface BuildingRepository {
    fun observeBuilding(externalId: String): Flow<Building?>
    suspend fun refreshBuilding(externalId: String, address: String, coordinate: Coordinate)
    suspend fun updateDomofonCode(entranceId: Long, code: String, success: Boolean)
    suspend fun getEntrances(externalId: String): Building?
}
