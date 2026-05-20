package com.pinpoint.app.domain.model

import java.time.LocalDateTime

data class CourierLocation(
    val courierId: Int,
    val latitude: Double,
    val longitude: Double,
    val updatedAt: LocalDateTime
)
