package com.pinpoint.app.data.mapper

import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.pinpoint.app.data.local.entity.TrajectoryEntity
import com.pinpoint.app.domain.model.LocationPoint
import com.pinpoint.app.domain.model.Trajectory

private val gson = Gson()
private val typeToken = object : TypeToken<List<LocationPoint>>() {}.type

fun TrajectoryEntity.toDomain(): Trajectory = Trajectory(
    id = id,
    buildingExternalId = buildingExternalId,
    courierId = courierId,
    deliveredAt = deliveredAt,
    points = gson.fromJson(dataPoints, typeToken)
)

fun Trajectory.toEntity(): TrajectoryEntity = TrajectoryEntity(
    id = id,
    buildingExternalId = buildingExternalId,
    courierId = courierId,
    deliveredAt = deliveredAt,
    dataPoints = gson.toJson(points, typeToken)
)
