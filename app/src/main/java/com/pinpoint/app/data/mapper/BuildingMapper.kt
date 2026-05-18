package com.pinpoint.app.data.mapper

import com.pinpoint.app.data.local.entity.BuildingEntity
import com.pinpoint.app.data.local.entity.EntranceEntity
import com.pinpoint.app.domain.model.Building
import com.pinpoint.app.domain.model.BuildingType
import com.pinpoint.app.domain.model.Coordinate
import com.pinpoint.app.domain.model.Entrance

fun BuildingEntity.toDomain(entrances: List<EntranceEntity>): Building = Building(
    id = id,
    externalId = buildingExternalId,
    address = address,
    coordinate = Coordinate(latitude, longitude),
    buildingType = BuildingType.entries.firstOrNull { it.displayName == buildingType }
        ?: BuildingType.OTHER,
    difficultyIndex = difficultyIndex,
    hasLift = hasLift,
    requiresChip = requiresChip,
    entranceHint = entranceHint,
    entrances = entrances.map { it.toDomain() },
    updatedAt = updatedAt
)

fun EntranceEntity.toDomain(): Entrance = Entrance(
    id = id,
    label = label,
    coordinate = Coordinate(latitude, longitude),
    domofonCode = domofonCode,
    hasBarrier = hasBarrier,
    validatedCount = validatedCount,
    lastValidatedAt = lastValidatedAt
)

fun Building.toEntity(): BuildingEntity = BuildingEntity(
    id = id,
    buildingExternalId = externalId,
    address = address,
    latitude = coordinate.latitude,
    longitude = coordinate.longitude,
    buildingType = buildingType.displayName,
    difficultyIndex = difficultyIndex,
    hasLift = hasLift,
    requiresChip = requiresChip,
    entranceHint = entranceHint,
    updatedAt = updatedAt
)

fun List<Entrance>.toEntities(buildingId: Long): List<EntranceEntity> = map {
    EntranceEntity(
        id = it.id,
        buildingId = buildingId,
        label = it.label,
        latitude = it.coordinate.latitude,
        longitude = it.coordinate.longitude,
        domofonCode = it.domofonCode,
        hasBarrier = it.hasBarrier,
        validatedCount = it.validatedCount,
        lastValidatedAt = it.lastValidatedAt
    )
}
