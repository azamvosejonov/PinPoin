package com.pinpoint.app.domain.model

data class IndoorMap(
    val id: Int,
    val buildingExternalId: String,
    val floorNumber: Int,
    val entrance: Int,
    val imageUrl: String?,
    val width: Int?,
    val height: Int?,
    val route: Route?
)

data class Route(
    val startPoint: Point,
    val endPoint: Point,
    val pathPoints: List<Point>,
    val distanceMeters: Double,
    val estimatedTimeSeconds: Int
)

data class Point(
    val x: Double,
    val y: Double,
    val label: String?
)

data class IndoorPathDetail(
    val id: Int,
    val buildingExternalId: String,
    val floorNumber: Int,
    val startX: Double,
    val startY: Double,
    val endX: Double,
    val endY: Double,
    val pathData: String
)

data class IndoorPathCreate(
    val floorNumber: Int,
    val startX: Double,
    val startY: Double,
    val endX: Double,
    val endY: Double,
    val pathData: String
)

data class IsometricTile(
    val x: Int,
    val y: Int,
    val type: TileType,
    val label: String? = null
)

enum class TileType {
    FLOOR,
    WALL,
    DOOR,
    ELEVATOR,
    STAIRS,
    APARTMENT,
    HIGHLIGHT_PATH,
    COURIER_POSITION
}
