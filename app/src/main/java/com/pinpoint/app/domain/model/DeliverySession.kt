package com.pinpoint.app.domain.model

data class DeliverySession(
    val id: Long,
    val orderId: String,
    val courierId: String,
    val buildingExternalId: String,
    val startTime: Long,
    val endTime: Long?,
    val temperatureModel: String,
    val startTemperature: Double,
    val predictedTemperature: Double,
    val predictedEta: Long,
    val transportMode: TransportMode?,
)
