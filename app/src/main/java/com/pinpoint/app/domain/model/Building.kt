package com.pinpoint.app.domain.model

data class Building(
    val id: Long,
    val externalId: String,
    val address: String,
    val coordinate: Coordinate,
    val buildingType: BuildingType,
    val difficultyIndex: Int,
    val hasLift: Boolean,
    val requiresChip: Boolean,
    val entranceHint: String?,
    val entrances: List<Entrance> = emptyList(),
    val updatedAt: Long,
)
