package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class OrderDto(
    @SerializedName("id") val id: Int,
    @SerializedName("order_code") val orderCode: String,
    @SerializedName("tracking_hash") val trackingHash: String,
    @SerializedName("status") val status: String,
    @SerializedName("courier_id") val courierId: Int?,
    @SerializedName("restaurant_id") val restaurantId: Int,
    @SerializedName("pickup_address") val pickupAddress: String?,
    @SerializedName("dropoff_address") val dropoffAddress: String?,
    @SerializedName("total_amount") val totalAmount: Double?,
    @SerializedName("payment_method") val paymentMethod: String?,
    @SerializedName("declined_courier_ids") val declinedCourierIds: String?,
    @SerializedName("compensation_paid") val compensationPaid: Boolean,
    @SerializedName("max_retries") val maxRetries: Int,
    @SerializedName("retry_count") val retryCount: Int,
    @SerializedName("initial_food_temp") val initialFoodTemp: Double? = null,
    @SerializedName("packaging_type") val packagingType: String? = null,
    @SerializedName("predicted_arrival_temp") val predictedArrivalTemp: Double? = null,
    @SerializedName("thermal_risk_level") val thermalRiskLevel: String? = null,
    @SerializedName("corrected_latitude") val correctedLatitude: Double? = null,
    @SerializedName("corrected_longitude") val correctedLongitude: Double? = null,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("accepted_at") val acceptedAt: String?,
    @SerializedName("picked_up_at") val pickedUpAt: String?,
    @SerializedName("delivered_at") val deliveredAt: String?,
    @SerializedName("canceled_at") val canceledAt: String?,
    @SerializedName("delivery_failed_at") val deliveryFailedAt: String?
)

data class OrderStatusUpdateDto(
    @SerializedName("status") val status: String
)

data class OrderDeclineDto(
    @SerializedName("reason") val reason: String
)

enum class OrderStatus(val value: String) {
    PENDING("PENDING"),
    ACCEPTED("ACCEPTED"),
    PICKED_UP("PICKED_UP"),
    DELIVERED("DELIVERED"),
    CANCELED("CANCELED"),
    DELIVERY_FAILED("DELIVERY_FAILED"),
    READY_FOR_PICKUP("READY_FOR_PICKUP"),
    UNASSIGNABLE("UNASSIGNABLE"),
    RETURNED_TO_RESTAURANT("RETURNED_TO_RESTAURANT");

    companion object {
        fun fromValue(value: String): OrderStatus {
            return values().find { it.value == value } ?: PENDING
        }
    }
}

enum class PaymentMethod(val value: String) {
    CASH("CASH"),
    CARD("CARD"),
    PREPAID("PREPAID");

    companion object {
        fun fromValue(value: String): PaymentMethod {
            return values().find { it.value == value } ?: CASH
        }
    }
}
