package com.pinpoint.app.data.repository

import com.pinpoint.app.data.remote.backend.BackendApi
import com.pinpoint.app.data.remote.backend.dto.*
import com.pinpoint.app.domain.model.Restaurant
import com.pinpoint.app.domain.model.CourierLocation
import com.pinpoint.app.domain.model.IndoorMap
import com.pinpoint.app.domain.model.IndoorPathCreate
import com.pinpoint.app.domain.model.IndoorPathDetail
import com.pinpoint.app.domain.model.User
import com.pinpoint.app.domain.model.UserRole
import com.pinpoint.app.domain.model.TokenPair
import com.pinpoint.app.domain.model.OrderTracking
import com.pinpoint.app.domain.repository.BackendRepository
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import javax.inject.Inject

class BackendRepositoryImpl @Inject constructor(
    private val backendApi: BackendApi
) : BackendRepository {

    private val dateFormatter = DateTimeFormatter.ISO_DATE_TIME

    override suspend fun register(
        email: String,
        password: String,
        fullName: String?,
        phone: String?,
        role: String?
    ): Result<User> {
        return try {
            val user = backendApi.register(
                AuthRegisterDto(email, password, fullName, phone, role)
            )
            Result.success(user.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun login(email: String, password: String): Result<TokenPair> {
        return try {
            val tokens = backendApi.login(AuthLoginDto(email, password))
            Result.success(tokens.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun refreshToken(refreshToken: String): Result<TokenPair> {
        return try {
            val tokens = backendApi.refreshToken(
                TokenPairDto("", refreshToken, "bearer")
            )
            Result.success(tokens.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun logout(accessToken: String, refreshToken: String): Result<Unit> {
        return try {
            backendApi.logout(TokenPairDto(accessToken, refreshToken, "bearer"))
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getMe(): Result<User> {
        return try {
            val user = backendApi.getMe()
            Result.success(user.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateLocation(latitude: Double, longitude: Double): Result<CourierLocation> {
        return try {
            val location = backendApi.updateLocation(
                CourierLocationUpdateDto(latitude, longitude)
            )
            Result.success(location.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getCourierLocation(courierId: Int): Result<CourierLocation> {
        return try {
            val location = backendApi.getCourierLocation(courierId)
            Result.success(location.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getRestaurants(): Result<List<Restaurant>> {
        return try {
            val restaurants = backendApi.getRestaurants()
            Result.success(restaurants.map { it.toDomainModel() })
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getRestaurant(restaurantId: Int): Result<Restaurant> {
        return try {
            val restaurant = backendApi.getRestaurant(restaurantId)
            Result.success(restaurant.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getIndoorMap(externalId: String, entrance: Int, floor: Int): Result<IndoorMap> {
        return try {
            val indoorMap = backendApi.getIndoorMap(externalId, entrance, floor)
            Result.success(indoorMap.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun createIndoorPath(externalId: String, path: IndoorPathCreate): Result<IndoorPathDetail> {
        return try {
            val result = backendApi.createIndoorPath(externalId, path.toDto())
            Result.success(result.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun submitTelemetry(externalId: String, telemetry: TelemetryDto): Result<Unit> {
        return try {
            backendApi.submitTelemetry(externalId, telemetry)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun markIndoorEnter(orderId: Int): Result<Unit> {
        return try {
            backendApi.markIndoorEnter(orderId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun markIndoorExit(orderId: Int): Result<Unit> {
        return try {
            backendApi.markIndoorExit(orderId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun correctPin(orderId: Int, textAddress: String, gpsLat: Double, gpsLon: Double): Result<Unit> {
        return try {
            backendApi.correctPin(orderId, PinCorrectionRequestDto(orderId, textAddress, gpsLat, gpsLon))
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getPublicTracking(trackingHash: String): Result<OrderTracking> {
        return try {
            val tracking = backendApi.getPublicTracking(trackingHash)
            Result.success(tracking.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // DTO to Domain Model conversions
    private fun UserDto.toDomainModel(): User {
        return User(
            id = id,
            email = email,
            fullName = fullName,
            phone = phone,
            role = UserRole.valueOf(role.uppercase()),
            isActive = isActive,
            createdAt = LocalDateTime.parse(createdAt, dateFormatter)
        )
    }

    private fun TokenPairDto.toDomainModel(): TokenPair {
        return TokenPair(
            accessToken = accessToken,
            refreshToken = refreshToken,
            tokenType = tokenType
        )
    }

    private fun CourierLocationDto.toDomainModel(): CourierLocation {
        return CourierLocation(
            courierId = courierId,
            latitude = latitude,
            longitude = longitude,
            updatedAt = LocalDateTime.parse(updatedAt, dateFormatter)
        )
    }

    private fun RestaurantDto.toDomainModel(): Restaurant {
        return Restaurant(
            id = id,
            name = name,
            address = address,
            phone = phone,
            logoUrl = logoUrl,
            ownerId = ownerId,
            createdAt = LocalDateTime.parse(createdAt, dateFormatter)
        )
    }

    private fun IndoorMapDto.toDomainModel(): IndoorMap {
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

    private fun RouteDto.toDomainModel(): com.pinpoint.app.domain.model.Route {
        return com.pinpoint.app.domain.model.Route(
            startPoint = startPoint.toDomainModel(),
            endPoint = endPoint.toDomainModel(),
            pathPoints = pathPoints.map { it.toDomainModel() },
            distanceMeters = distanceMeters,
            estimatedTimeSeconds = estimatedTimeSeconds
        )
    }

    private fun PointDto.toDomainModel(): com.pinpoint.app.domain.model.Point {
        return com.pinpoint.app.domain.model.Point(x = x, y = y, label = label)
    }

    private fun IndoorPathDetailDto.toDomainModel(): IndoorPathDetail {
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

    private fun OrderTrackingDto.toDomainModel(): OrderTracking {
        return OrderTracking(
            orderCode = orderCode,
            status = com.pinpoint.app.domain.model.OrderStatus.valueOf(status.uppercase()),
            courierId = courierId,
            courierName = courierName,
            pickupAddress = pickupAddress,
            dropoffAddress = dropoffAddress,
            createdAt = LocalDateTime.parse(createdAt, dateFormatter),
            acceptedAt = acceptedAt?.let { LocalDateTime.parse(it, dateFormatter) },
            pickedUpAt = pickedUpAt?.let { LocalDateTime.parse(it, dateFormatter) },
            deliveredAt = deliveredAt?.let { LocalDateTime.parse(it, dateFormatter) },
            estimatedDelivery = estimatedDelivery?.let { LocalDateTime.parse(it, dateFormatter) }
        )
    }
}
