package com.pinpoint.app.ui

import com.pinpoint.app.domain.model.Building
import com.pinpoint.app.domain.model.Coordinate
import com.pinpoint.app.domain.model.ThermalProjection
import com.pinpoint.app.domain.usecase.ThermalRouteAdvice

data class PinPoIntState(
    val building: Building? = null,
    val adjustedCoordinate: Coordinate? = null,
    val projection: ThermalProjection? = null,
    val thermalAdvice: ThermalRouteAdvice? = null,
    val alerts: List<String> = emptyList(),
    val domofonCode: String? = null,
    val isOffline: Boolean = false
)
