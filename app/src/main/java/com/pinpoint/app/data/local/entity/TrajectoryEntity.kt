package com.pinpoint.app.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "trajectories")
data class TrajectoryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "building_external_id") val buildingExternalId: String,
    @ColumnInfo(name = "courier_id") val courierId: String,
    @ColumnInfo(name = "delivered_at") val deliveredAt: Long,
    @ColumnInfo(name = "data_points") val dataPoints: String,
)
