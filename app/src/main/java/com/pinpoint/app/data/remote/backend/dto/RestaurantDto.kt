package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class RestaurantDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("address") val address: String,
    @SerializedName("phone") val phone: String?,
    @SerializedName("logo_url") val logoUrl: String?,
    @SerializedName("owner_id") val ownerId: Int,
    @SerializedName("created_at") val createdAt: String
)
