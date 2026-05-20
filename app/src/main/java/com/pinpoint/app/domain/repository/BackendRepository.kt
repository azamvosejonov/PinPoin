package com.pinpoint.app.domain.repository

import com.pinpoint.app.domain.model.Restaurant
import com.pinpoint.app.domain.model.CourierLocation
import com.pinpoint.app.domain.model.IndoorMap
import com.pinpoint.app.domain.model.IndoorPathCreate
import com.pinpoint.app.domain.model.IndoorPathDetail
import com.pinpoint.app.domain.model.User
import com.pinpoint.app.domain.model.UserRole
import com.pinpoint.app.domain.model.TokenPair
import com.pinpoint.app.domain.model.OrderTracking
import com.pinpoint.app.data.remote.backend.dto.TelemetryDto

interface BackendRepository {
    // Auth
    suspend fun register(email: String, password: String, fullName: String?, phone: String?, role: String?): Result<User>
    suspend fun login(email: String, password: String): Result<TokenPair>
    suspend fun refreshToken(refreshToken: String): Result<TokenPair>
    suspend fun logout(accessToken: String, refreshToken: String): Result<Unit>
    suspend fun getMe(): Result<User>

    // Courier Location
    suspend fun updateLocation(latitude: Double, longitude: Double): Result<CourierLocation>
    suspend fun getCourierLocation(courierId: Int): Result<CourierLocation>

    // Restaurant
    suspend fun getRestaurants(): Result<List<Restaurant>>
    suspend fun getRestaurant(restaurantId: Int): Result<Restaurant>

    // Indoor Map
    suspend fun getIndoorMap(externalId: String, entrance: Int, floor: Int): Result<IndoorMap>
    suspend fun createIndoorPath(externalId: String, path: IndoorPathCreate): Result<IndoorPathDetail>
    suspend fun submitTelemetry(externalId: String, telemetry: TelemetryDto): Result<Unit>

    // Indoor timing
    suspend fun markIndoorEnter(orderId: Int): Result<Unit>
    suspend fun markIndoorExit(orderId: Int): Result<Unit>

    // Pin correction
    suspend fun correctPin(orderId: Int, textAddress: String, gpsLat: Double, gpsLon: Double): Result<Unit>

    // Public Tracking
    suspend fun getPublicTracking(trackingHash: String): Result<OrderTracking>
}
