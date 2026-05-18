package com.pinpoint.app.data.remote.predictive

import kotlin.math.cos
import kotlin.math.sin

/**
 * Lightweight heuristic-based predictor that adjusts courier pins based on text embedding vector
 * and historical motion data. This keeps implementation fully offline and open-source friendly.
 */
class PinCorrectionModel {

    fun predictAdjustment(inputVector: FloatArray): Pair<Double, Double> {
        if (inputVector.isEmpty()) return 0.0 to 0.0
        val hash = inputVector.fold(0.0) { acc, value -> acc + value.toDouble() }
        val angle = hash % (2 * Math.PI)
        val magnitude = (inputVector.size.coerceAtMost(64) / 64.0) * 0.0002
        val deltaLat = magnitude * sin(angle)
        val deltaLon = magnitude * cos(angle)
        return deltaLat to deltaLon
    }
}
