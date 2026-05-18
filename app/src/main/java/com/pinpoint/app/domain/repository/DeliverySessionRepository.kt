package com.pinpoint.app.domain.repository

import com.pinpoint.app.domain.model.DeliverySession
import kotlinx.coroutines.flow.Flow

interface DeliverySessionRepository {
    suspend fun startSession(session: DeliverySession): Long
    suspend fun updateSession(session: DeliverySession)
    suspend fun getSession(orderId: String): DeliverySession?
    fun observeLatestSession(courierId: String): Flow<DeliverySession?>
}
