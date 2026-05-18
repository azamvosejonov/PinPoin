package com.pinpoint.app.data.repository

import com.pinpoint.app.data.local.dao.BuildingDao
import com.pinpoint.app.data.mapper.toDomain
import com.pinpoint.app.data.mapper.toEntities
import com.pinpoint.app.data.remote.backend.BackendApi
import com.pinpoint.app.data.remote.backend.dto.BuildingUpsertRequest
import com.pinpoint.app.data.remote.backend.dto.CoordinateDto
import com.pinpoint.app.data.remote.backend.dto.EntranceCreateDto
import com.pinpoint.app.data.remote.backend.dto.DomofonValidationRequestDto
import com.pinpoint.app.domain.model.Building
import com.pinpoint.app.domain.model.Coordinate
import com.pinpoint.app.domain.repository.BuildingRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onStart
import java.time.Instant
import java.time.format.DateTimeFormatter
import javax.inject.Inject

class BuildingRepositoryImpl @Inject constructor(
    private val buildingDao: BuildingDao,
    private val backendApi: BackendApi
) : BuildingRepository {

    override fun observeBuilding(externalId: String): Flow<Building?> = buildingDao
        .observeBuildingByExternalId(externalId)
        .flatMapLatest { entity ->
            if (entity == null) {
                kotlinx.coroutines.flow.flowOf(null)
            } else {
                buildingDao.observeEntrancesByBuilding(entity.id)
                    .map { entrances -> entity.toDomain(entrances) }
                    .onStart { emit(entity.toDomain(emptyList())) }
            }
        }

    override suspend fun refreshBuilding(externalId: String, address: String, coordinate: Coordinate) {
        val remote = runCatching { backendApi.getBuilding(externalId) }.getOrNull()
        if (remote != null) {
            val buildingEntity = com.pinpoint.app.data.local.entity.BuildingEntity(
                id = remote.id,
                buildingExternalId = remote.externalId,
                address = remote.address,
                latitude = remote.coordinate.latitude,
                longitude = remote.coordinate.longitude,
                buildingType = remote.buildingType,
                difficultyIndex = remote.difficultyIndex,
                hasLift = remote.hasLift,
                requiresChip = remote.requiresChip,
                entranceHint = remote.entranceHint,
                updatedAt = System.currentTimeMillis()
            )
            val buildingId = buildingDao.upsertBuilding(buildingEntity)
            val entranceEntities = remote.entrances.map {
                com.pinpoint.app.data.local.entity.EntranceEntity(
                    id = it.id,
                    buildingId = buildingId,
                    label = it.label,
                    latitude = it.latitude,
                    longitude = it.longitude,
                    domofonCode = it.domofonCode,
                    hasBarrier = it.hasBarrier,
                    validatedCount = it.validatedCount,
                    lastValidatedAt = it.lastValidatedAt?.let { ts -> Instant.from(DateTimeFormatter.ISO_DATE_TIME.parse(ts)).toEpochMilli() } ?: 0L
                )
            }
            buildingDao.upsertEntrances(entranceEntities)
            return
        }

        val existing = buildingDao.getBuildingByExternalId(externalId)
        val timestamp = System.currentTimeMillis()
        val entity = existing?.copy(
            address = address,
            latitude = coordinate.latitude,
            longitude = coordinate.longitude,
            updatedAt = timestamp
        ) ?: com.pinpoint.app.data.local.entity.BuildingEntity(
            buildingExternalId = externalId,
            address = address,
            latitude = coordinate.latitude,
            longitude = coordinate.longitude,
            buildingType = com.pinpoint.app.domain.model.BuildingType.OTHER.displayName,
            difficultyIndex = 1,
            hasLift = false,
            requiresChip = false,
            entranceHint = null,
            updatedAt = timestamp
        )
        val id = buildingDao.upsertBuilding(entity)
        if (existing == null) {
            buildingDao.upsertEntrances(
                listOf(
                    com.pinpoint.app.data.local.entity.EntranceEntity(
                        buildingId = id,
                        label = "1",
                        latitude = coordinate.latitude,
                        longitude = coordinate.longitude,
                        domofonCode = null,
                        hasBarrier = false,
                        validatedCount = 0,
                        lastValidatedAt = timestamp
                    )
                )
            )
        }

        runCatching {
            backendApi.upsertBuilding(
                BuildingUpsertRequest(
                    externalId = externalId,
                    address = address,
                    coordinate = CoordinateDto(coordinate.latitude, coordinate.longitude),
                    buildingType = entity.buildingType,
                    difficultyIndex = entity.difficultyIndex,
                    hasLift = entity.hasLift,
                    requiresChip = entity.requiresChip,
                    entranceHint = entity.entranceHint,
                    entrances = listOf(
                        EntranceCreateDto(
                            label = "1",
                            latitude = coordinate.latitude,
                            longitude = coordinate.longitude,
                            domofonCode = null,
                            hasBarrier = false,
                            validatedCount = 0,
                            lastValidatedAt = null
                        )
                    )
                )
            )
        }
    }

    override suspend fun updateDomofonCode(entranceId: Long, code: String, success: Boolean) {
        if (success) {
            buildingDao.updateDomofonCode(entranceId, code, System.currentTimeMillis())
        } else {
            buildingDao.markDomofonFailure(entranceId)
        }
        runCatching {
            backendApi.validateDomofon(
                entranceId,
                DomofonValidationRequestDto(code = code, success = success)
            )
        }
    }

    override suspend fun getEntrances(externalId: String): Building? {
        val entity = buildingDao.getBuildingByExternalId(externalId) ?: return null
        val entrances = buildingDao.getEntrancesForBuilding(entity.id)
        return entity.toDomain(entrances)
    }
}
