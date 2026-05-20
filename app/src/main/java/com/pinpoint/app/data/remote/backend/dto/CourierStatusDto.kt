package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class CourierStatusDto(
    @SerializedName("courier_id") val courierId: Int,
    @SerializedName("status") val status: String,
    @SerializedName("transport_mode") val transportMode: String? = "pedestrian",
    @SerializedName("updated_at") val updatedAt: String,
    @SerializedName("last_online_at") val lastOnlineAt: String?,
    @SerializedName("cash_balance") val cashBalance: Double
)

data class CourierStatusUpdateDto(
    @SerializedName("status") val status: String,
    @SerializedName("transport_mode") val transportMode: String? = null
)

data class CourierCashCollectDto(
    @SerializedName("amount") val amount: Double
)

enum class CourierStatusEnum(val value: String) {
    OFFLINE("offline"),
    ONLINE("online"),
    BUSY("busy"),
    ON_BREAK("on_break");

    companion object {
        fun fromValue(value: String): CourierStatusEnum {
            return values().find { it.value == value } ?: OFFLINE
        }
    }
}
