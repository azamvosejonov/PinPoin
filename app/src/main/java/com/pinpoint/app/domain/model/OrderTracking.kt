package com.pinpoint.app.domain.model

import java.time.LocalDateTime

data class OrderTracking(
    val orderCode: String,
    val status: OrderStatus,
    val courierId: Int?,
    val courierName: String?,
    val pickupAddress: String?,
    val dropoffAddress: String?,
    val createdAt: LocalDateTime,
    val acceptedAt: LocalDateTime?,
    val pickedUpAt: LocalDateTime?,
    val deliveredAt: LocalDateTime?,
    val estimatedDelivery: LocalDateTime?
)
