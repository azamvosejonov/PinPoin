package com.pinpoint.app.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "entrances",
    foreignKeys = [
        ForeignKey(
            entity = BuildingEntity::class,
            parentColumns = ["id"],
            childColumns = ["building_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index(value = ["building_id"])]
)
data class EntranceEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "building_id") val buildingId: Long,
    @ColumnInfo(name = "label") val label: String,
    @ColumnInfo(name = "latitude") val latitude: Double,
    @ColumnInfo(name = "longitude") val longitude: Double,
    @ColumnInfo(name = "domofon_code") val domofonCode: String?,
    @ColumnInfo(name = "has_barrier") val hasBarrier: Boolean,
    @ColumnInfo(name = "validated_count") val validatedCount: Int,
    @ColumnInfo(name = "last_validated_at") val lastValidatedAt: Long,
)
