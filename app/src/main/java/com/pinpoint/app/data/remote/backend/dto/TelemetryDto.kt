package com.pinpoint.app.data.remote.backend.dto

data class TelemetryDto(
    val orderId: Int,
    val courierId: Int,
    val entrance: Int,
    val floor: Int,
    val trajectory: List<IndoorTelemetryPointDto>,
    val timestamp: Long
)

data class IndoorTelemetryPointDto(
    val x: Double,
    val y: Double,
    val z: Double,
    val timestamp: Long,
    val accuracy: Double
)
