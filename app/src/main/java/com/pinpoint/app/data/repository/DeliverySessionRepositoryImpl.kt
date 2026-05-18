package com.pinpoint.app.data.repository

import com.pinpoint.app.data.local.dao.DeliverySessionDao
import com.pinpoint.app.data.local.entity.DeliverySessionEntity
import com.pinpoint.app.domain.model.DeliverySession
import com.pinpoint.app.domain.repository.DeliverySessionRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

class DeliverySessionRepositoryImpl @Inject constructor(
    private val dao: DeliverySessionDao
) : DeliverySessionRepository {

    override suspend fun startSession(session: DeliverySession): Long {
        val id = dao.insertSession(session.toEntity())
        return if (id == 0L) session.id else id
    }

    override suspend fun updateSession(session: DeliverySession) {
        dao.updateSession(session.toEntity())
    }

    override suspend fun getSession(orderId: String): DeliverySession? =
        dao.getSessionByOrderId(orderId)?.toDomain()

    override fun observeLatestSession(courierId: String): Flow<DeliverySession?> =
        dao.observeLatestSession(courierId).map { it?.toDomain() }
}

private fun DeliverySessionEntity.toDomain(): DeliverySession = DeliverySession(
    id = id,
    orderId = orderId,
    courierId = courierId,
    buildingExternalId = buildingExternalId,
    startTime = startTime,
    endTime = endTime,
    temperatureModel = temperatureModel,
    startTemperature = startTemperature,
    predictedTemperature = predictedTemperature,
    predictedEta = predictedEta,
    transportMode = transportMode?.let {
        runCatching { com.pinpoint.app.domain.model.TransportMode.valueOf(it) }.getOrDefault(
            com.pinpoint.app.domain.model.TransportMode.UNKNOWN
        )
    }
)

private fun DeliverySession.toEntity(): DeliverySessionEntity = DeliverySessionEntity(
    id = id,
    orderId = orderId,
    courierId = courierId,
    buildingExternalId = buildingExternalId,
    startTime = startTime,
    endTime = endTime,
    temperatureModel = temperatureModel,
    startTemperature = startTemperature,
    predictedTemperature = predictedTemperature,
    predictedEta = predictedEta,
    transportMode = transportMode?.name
)
