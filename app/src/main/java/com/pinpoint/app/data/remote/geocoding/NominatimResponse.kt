package com.pinpoint.app.data.remote.geocoding

import com.google.gson.annotations.SerializedName

data class NominatimResponse(
    @SerializedName("place_id") val placeId: Long,
    @SerializedName("display_name") val displayName: String?,
    val lat: String,
    val lon: String,
    @SerializedName("type") val type: String?,
    @SerializedName("importance") val importance: Double?
)
