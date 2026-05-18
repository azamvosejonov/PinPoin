package com.pinpoint.app.domain.usecase

import com.pinpoint.app.data.remote.backend.BackendRemoteDataSource
import com.pinpoint.app.data.remote.backend.dto.CoordinateDto
import com.pinpoint.app.data.remote.backend.dto.PredictivePinRequestDto
import com.pinpoint.app.domain.model.Coordinate
import kotlin.math.cos
import kotlin.math.sin
import javax.inject.Inject

class PredictivePinDropUseCase @Inject constructor(
    private val backendRemoteDataSource: BackendRemoteDataSource
) {

    suspend fun adjustPin(
        rawCoordinate: Coordinate,
        addressEmbedding: FloatArray,
        historicalVector: FloatArray
    ): Coordinate {
        val request = PredictivePinRequestDto(
            rawCoordinate = CoordinateDto(rawCoordinate.latitude, rawCoordinate.longitude),
            addressEmbedding = addressEmbedding.toList(),
            historicalVector = historicalVector.toList()
        )

        val response = runCatching { backendRemoteDataSource.predictivePin(request) }.getOrNull()
        if (response != null) {
            return Coordinate(
                response.adjustedCoordinate.latitude,
                response.adjustedCoordinate.longitude
            )
        }

        val fallback = addressEmbedding.toList() + historicalVector.toList()
        if (fallback.isEmpty()) return rawCoordinate
        val hash = fallback.fold(0.0) { acc, value -> acc + value }
        val angle = hash % (2 * Math.PI)
        val magnitude = (fallback.size.coerceAtMost(64) / 64.0) * 0.0002
        val deltaLat = magnitude * sin(angle)
        val deltaLon = magnitude * cos(angle)
        return Coordinate(rawCoordinate.latitude + deltaLat, rawCoordinate.longitude + deltaLon)
    }
}
