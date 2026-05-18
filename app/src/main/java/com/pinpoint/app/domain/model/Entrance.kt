package com.pinpoint.app.domain.model

data class Entrance(
    val id: Long,
    val label: String,
    val coordinate: Coordinate,
    val domofonCode: String?,
    val hasBarrier: Boolean,
    val validatedCount: Int,
    val lastValidatedAt: Long
)
