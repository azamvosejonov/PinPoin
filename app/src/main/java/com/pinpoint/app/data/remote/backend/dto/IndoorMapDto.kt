package com.pinpoint.app.data.remote.backend.dto

import com.google.gson.annotations.SerializedName
import com.pinpoint.app.domain.model.IndoorMap
import com.pinpoint.app.domain.model.IndoorPathDetail
import com.pinpoint.app.domain.model.IndoorPathCreate
import com.pinpoint.app.domain.model.Point
import com.pinpoint.app.domain.model.Route

data class IndoorMapDto(
    @SerializedName("id") val id: Int,
    @SerializedName("building_external_id") val buildingExternalId: String,
    @SerializedName("floor_number") val floorNumber: Int,
    @SerializedName("entrance") val entrance: Int,
    @SerializedName("image_url") val imageUrl: String?,
    @SerializedName("width") val width: Int?,
    @SerializedName("height") val height: Int?,
    @SerializedName("route") val route: RouteDto?
)

data class RouteDto(
    @SerializedName("start_point") val startPoint: PointDto,
    @SerializedName("end_point") val endPoint: PointDto,
    @SerializedName("path_points") val pathPoints: List<PointDto>,
    @SerializedName("distance_meters") val distanceMeters: Double,
    @SerializedName("estimated_time_seconds") val estimatedTimeSeconds: Int
)

data class PointDto(
    @SerializedName("x") val x: Double,
    @SerializedName("y") val y: Double,
    @SerializedName("label") val label: String?
)

fun IndoorMapDto.toDomainModel(): IndoorMap {
    return IndoorMap(
        id = id,
        buildingExternalId = buildingExternalId,
        floorNumber = floorNumber,
        entrance = entrance,
        imageUrl = imageUrl,
        width = width,
        height = height,
        route = route?.toDomainModel()
    )
}

fun RouteDto.toDomainModel(): Route {
    return Route(
        startPoint = startPoint.toDomainModel(),
        endPoint = endPoint.toDomainModel(),
        pathPoints = pathPoints.map { it.toDomainModel() },
        distanceMeters = distanceMeters,
        estimatedTimeSeconds = estimatedTimeSeconds
    )
}

fun PointDto.toDomainModel(): Point {
    return Point(
        x = x,
        y = y,
        label = label
    )
}

data class IndoorPathDetailDto(
    @SerializedName("id") val id: Int,
    @SerializedName("building_external_id") val buildingExternalId: String,
    @SerializedName("floor_number") val floorNumber: Int,
    @SerializedName("start_x") val startX: Double,
    @SerializedName("start_y") val startY: Double,
    @SerializedName("end_x") val endX: Double,
    @SerializedName("end_y") val endY: Double,
    @SerializedName("path_data") val pathData: String
)

data class IndoorPathCreateDto(
    @SerializedName("floor_number") val floorNumber: Int,
    @SerializedName("start_x") val startX: Double,
    @SerializedName("start_y") val startY: Double,
    @SerializedName("end_x") val endX: Double,
    @SerializedName("end_y") val endY: Double,
    @SerializedName("path_data") val pathData: String
)

fun IndoorPathDetailDto.toDomainModel(): IndoorPathDetail {
    return IndoorPathDetail(
        id = id,
        buildingExternalId = buildingExternalId,
        floorNumber = floorNumber,
        startX = startX,
        startY = startY,
        endX = endX,
        endY = endY,
        pathData = pathData
    )
}

fun IndoorPathCreate.toDto(): IndoorPathCreateDto {
    return IndoorPathCreateDto(
        floorNumber = floorNumber,
        startX = startX,
        startY = startY,
        endX = endX,
        endY = endY,
        pathData = pathData
    )
}
