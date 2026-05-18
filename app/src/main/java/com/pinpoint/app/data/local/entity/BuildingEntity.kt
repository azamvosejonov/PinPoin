package com.pinpoint.app.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "buildings")
data class BuildingEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "building_external_id") val buildingExternalId: String,
    val address: String,
    @ColumnInfo(name = "latitude") val latitude: Double,
    @ColumnInfo(name = "longitude") val longitude: Double,
    @ColumnInfo(name = "building_type") val buildingType: String,
    @ColumnInfo(name = "difficulty_index") val difficultyIndex: Int,
    @ColumnInfo(name = "has_lift") val hasLift: Boolean,
    @ColumnInfo(name = "requires_chip") val requiresChip: Boolean,
    @ColumnInfo(name = "entrance_hint") val entranceHint: String?,
    @ColumnInfo(name = "updated_at") val updatedAt: Long,
)
