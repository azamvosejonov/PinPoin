package com.pinpoint.app.domain.model

data class Trajectory(
    val id: Long,
    val buildingExternalId: String,
    val courierId: String,
    val deliveredAt: Long,
    val points: List<LocationPoint>
)
