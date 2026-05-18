package com.pinpoint.app.domain.model

data class LocationPoint(
    val latitude: Double,
    val longitude: Double,
    val timestamp: Long,
    val speed: Float?,
    val bearing: Float?
)
