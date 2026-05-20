package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class OrderTrackingDto(
    @SerializedName("order_code") val orderCode: String,
    @SerializedName("status") val status: String,
    @SerializedName("courier_id") val courierId: Int?,
    @SerializedName("courier_name") val courierName: String?,
    @SerializedName("pickup_address") val pickupAddress: String?,
    @SerializedName("dropoff_address") val dropoffAddress: String?,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("accepted_at") val acceptedAt: String?,
    @SerializedName("picked_up_at") val pickedUpAt: String?,
    @SerializedName("delivered_at") val deliveredAt: String?,
    @SerializedName("estimated_delivery") val estimatedDelivery: String?
)
