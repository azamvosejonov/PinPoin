package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName

data class BuildingDto(
    val id: Long,
    @SerializedName("external_id") val externalId: String,
    val address: String,
    @SerializedName("coordinate") val coordinate: CoordinateDto,
    @SerializedName("building_type") val buildingType: String,
    @SerializedName("difficulty_index") val difficultyIndex: Int,
    @SerializedName("has_lift") val hasLift: Boolean,
    @SerializedName("requires_chip") val requiresChip: Boolean,
    @SerializedName("entrance_hint") val entranceHint: String?,
    val entrances: List<EntranceDto> = emptyList(),
    @SerializedName("updated_at") val updatedAt: String
)

data class EntranceDto(
    val id: Long,
    val label: String,
    val latitude: Double,
    val longitude: Double,
    @SerializedName("domofon_code") val domofonCode: String?,
    @SerializedName("has_barrier") val hasBarrier: Boolean,
    @SerializedName("validated_count") val validatedCount: Int,
    @SerializedName("last_validated_at") val lastValidatedAt: String?
)

data class BuildingUpsertRequest(
    @SerializedName("external_id") val externalId: String,
    val address: String,
    val coordinate: CoordinateDto,
    @SerializedName("building_type") val buildingType: String,
    @SerializedName("difficulty_index") val difficultyIndex: Int,
    @SerializedName("has_lift") val hasLift: Boolean,
    @SerializedName("requires_chip") val requiresChip: Boolean,
    @SerializedName("entrance_hint") val entranceHint: String?,
    val entrances: List<EntranceCreateDto>
)

data class EntranceCreateDto(
    val label: String,
    val latitude: Double,
    val longitude: Double,
    @SerializedName("domofon_code") val domofonCode: String?,
    @SerializedName("has_barrier") val hasBarrier: Boolean,
    @SerializedName("validated_count") val validatedCount: Int,
    @SerializedName("last_validated_at") val lastValidatedAt: String?
)
