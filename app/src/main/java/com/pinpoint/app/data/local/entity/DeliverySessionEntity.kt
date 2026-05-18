package com.pinpoint.app.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "delivery_sessions")
data class DeliverySessionEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "order_id") val orderId: String,
    @ColumnInfo(name = "courier_id") val courierId: String,
    @ColumnInfo(name = "building_external_id") val buildingExternalId: String,
    @ColumnInfo(name = "start_time") val startTime: Long,
    @ColumnInfo(name = "end_time") val endTime: Long?,
    @ColumnInfo(name = "temperature_model") val temperatureModel: String,
    @ColumnInfo(name = "start_temperature") val startTemperature: Double,
    @ColumnInfo(name = "predicted_temperature") val predictedTemperature: Double,
    @ColumnInfo(name = "predicted_eta") val predictedEta: Long,
    @ColumnInfo(name = "transport_mode") val transportMode: String?,
)
