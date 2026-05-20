package com.pinpoint.app.domain.model

import java.time.LocalDateTime

data class Order(
    val id: Int,
    val orderCode: String,
    val trackingHash: String,
    val status: OrderStatus,
    val courierId: Int?,
    val restaurantId: Int,
    val pickupAddress: String?,
    val dropoffAddress: String?,
    val totalAmount: Double?,
    val paymentMethod: PaymentMethod,
    val declinedCourierIds: String?,
    val compensationPaid: Boolean,
    val maxRetries: Int,
    val retryCount: Int,
    val initialFoodTemp: Double? = null,
    val packagingType: String? = null,
    val predictedArrivalTemp: Double? = null,
    val thermalRiskLevel: String? = null,
    val correctedLatitude: Double? = null,
    val correctedLongitude: Double? = null,
    val createdAt: LocalDateTime,
    val acceptedAt: LocalDateTime?,
    val pickedUpAt: LocalDateTime?,
    val deliveredAt: LocalDateTime?,
    val canceledAt: LocalDateTime?,
    val deliveryFailedAt: LocalDateTime?
)

data class CourierStatus(
    val courierId: Int,
    val status: CourierStatusEnum,
    val transportMode: TransportMode = TransportMode.FOOT,
    val updatedAt: LocalDateTime,
    val lastOnlineAt: LocalDateTime?,
    val cashBalance: Double
)

enum class OrderStatus {
    PENDING,
    ACCEPTED,
    PICKED_UP,
    DELIVERED,
    CANCELED,
    DELIVERY_FAILED,
    READY_FOR_PICKUP,
    UNASSIGNABLE,
    RETURNED_TO_RESTAURANT
}

enum class PaymentMethod {
    CASH,
    CARD,
    PREPAID
}

enum class CourierStatusEnum {
    OFFLINE,
    ONLINE,
    BUSY,
    ON_BREAK
}
