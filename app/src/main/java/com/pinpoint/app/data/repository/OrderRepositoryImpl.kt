package com.pinpoint.app.data.repository

import com.pinpoint.app.data.remote.backend.BackendApi
import com.pinpoint.app.data.remote.backend.dto.OrderDto
import com.pinpoint.app.data.remote.backend.dto.OrderStatusUpdateDto
import com.pinpoint.app.data.remote.backend.dto.OrderDeclineDto
import com.pinpoint.app.data.remote.backend.dto.CourierStatusDto
import com.pinpoint.app.data.remote.backend.dto.CourierStatusUpdateDto
import com.pinpoint.app.data.remote.backend.dto.CourierCashCollectDto
import com.pinpoint.app.data.remote.backend.dto.OrderStatus as OrderStatusDto
import com.pinpoint.app.data.remote.backend.dto.CourierStatusEnum as CourierStatusEnumDto
import com.pinpoint.app.data.remote.backend.dto.PaymentMethod as PaymentMethodDto
import com.pinpoint.app.domain.model.Order
import com.pinpoint.app.domain.model.CourierStatus
import com.pinpoint.app.domain.model.OrderStatus
import com.pinpoint.app.domain.model.CourierStatusEnum
import com.pinpoint.app.domain.model.PaymentMethod
import com.pinpoint.app.domain.model.TransportMode
import com.pinpoint.app.domain.repository.OrderRepository
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import javax.inject.Inject

class OrderRepositoryImpl @Inject constructor(
    private val backendApi: BackendApi
) : OrderRepository {

    private val dateFormatter = DateTimeFormatter.ISO_DATE_TIME

    override suspend fun getMyOrders(): Result<List<Order>> {
        return try {
            val orders = backendApi.getMyOrders()
            Result.success(orders.map { it.toDomainModel() })
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getOrder(orderId: Int): Result<Order> {
        return try {
            val order = backendApi.getOrder(orderId)
            Result.success(order.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateOrderStatus(orderId: Int, status: OrderStatus): Result<Order> {
        return try {
            val order = backendApi.updateOrderStatus(
                orderId,
                OrderStatusUpdateDto(status.name)
            )
            Result.success(order.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun declineOrder(orderId: Int, reason: String): Result<Order> {
        return try {
            val order = backendApi.declineOrder(
                orderId,
                OrderDeclineDto(reason)
            )
            Result.success(order.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateCourierStatus(status: CourierStatusEnum): Result<CourierStatus> {
        return try {
            val courierStatus = backendApi.updateCourierStatus(
                CourierStatusUpdateDto(status.name.lowercase())
            )
            Result.success(courierStatus.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getCourierStatus(courierId: Int): Result<CourierStatus> {
        return try {
            val courierStatus = backendApi.getCourierStatus(courierId)
            Result.success(courierStatus.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun collectCash(courierId: Int, amount: Double): Result<CourierStatus> {
        return try {
            val courierStatus = backendApi.collectCash(
                courierId,
                CourierCashCollectDto(amount)
            )
            Result.success(courierStatus.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun OrderDto.toDomainModel(): Order {
        return Order(
            id = id,
            orderCode = orderCode,
            trackingHash = trackingHash,
            status = OrderStatusDto.fromValue(status).toDomainModel(),
            courierId = courierId,
            restaurantId = restaurantId,
            pickupAddress = pickupAddress,
            dropoffAddress = dropoffAddress,
            totalAmount = totalAmount,
            paymentMethod = paymentMethod?.let { PaymentMethodDto.fromValue(it).toDomainModel() } ?: PaymentMethod.CASH,
            declinedCourierIds = declinedCourierIds,
            compensationPaid = compensationPaid,
            maxRetries = maxRetries,
            retryCount = retryCount,
            initialFoodTemp = initialFoodTemp,
            packagingType = packagingType,
            predictedArrivalTemp = predictedArrivalTemp,
            thermalRiskLevel = thermalRiskLevel,
            correctedLatitude = correctedLatitude,
            correctedLongitude = correctedLongitude,
            createdAt = LocalDateTime.parse(createdAt, dateFormatter),
            acceptedAt = acceptedAt?.let { LocalDateTime.parse(it, dateFormatter) },
            pickedUpAt = pickedUpAt?.let { LocalDateTime.parse(it, dateFormatter) },
            deliveredAt = deliveredAt?.let { LocalDateTime.parse(it, dateFormatter) },
            canceledAt = canceledAt?.let { LocalDateTime.parse(it, dateFormatter) },
            deliveryFailedAt = deliveryFailedAt?.let { LocalDateTime.parse(it, dateFormatter) }
        )
    }

    private fun CourierStatusDto.toDomainModel(): CourierStatus {
        return CourierStatus(
            courierId = courierId,
            status = CourierStatusEnumDto.fromValue(status).toDomainModel(),
            transportMode = mapTransportMode(transportMode),
            updatedAt = LocalDateTime.parse(updatedAt, dateFormatter),
            lastOnlineAt = lastOnlineAt?.let { LocalDateTime.parse(it, dateFormatter) },
            cashBalance = cashBalance
        )
    }

    private fun mapTransportMode(mode: String?): TransportMode {
        return when (mode) {
            "pedestrian" -> TransportMode.FOOT
            "bicycle" -> TransportMode.BICYCLE
            "car" -> TransportMode.VEHICLE
            else -> TransportMode.UNKNOWN
        }
    }

    private fun OrderStatusDto.toDomainModel(): OrderStatus {
        return when (this) {
            OrderStatusDto.PENDING -> OrderStatus.PENDING
            OrderStatusDto.ACCEPTED -> OrderStatus.ACCEPTED
            OrderStatusDto.PICKED_UP -> OrderStatus.PICKED_UP
            OrderStatusDto.DELIVERED -> OrderStatus.DELIVERED
            OrderStatusDto.CANCELED -> OrderStatus.CANCELED
            OrderStatusDto.DELIVERY_FAILED -> OrderStatus.DELIVERY_FAILED
            OrderStatusDto.READY_FOR_PICKUP -> OrderStatus.READY_FOR_PICKUP
            OrderStatusDto.UNASSIGNABLE -> OrderStatus.UNASSIGNABLE
            OrderStatusDto.RETURNED_TO_RESTAURANT -> OrderStatus.RETURNED_TO_RESTAURANT
        }
    }

    private fun CourierStatusEnumDto.toDomainModel(): CourierStatusEnum {
        return when (this) {
            CourierStatusEnumDto.OFFLINE -> CourierStatusEnum.OFFLINE
            CourierStatusEnumDto.ONLINE -> CourierStatusEnum.ONLINE
            CourierStatusEnumDto.BUSY -> CourierStatusEnum.BUSY
            CourierStatusEnumDto.ON_BREAK -> CourierStatusEnum.ON_BREAK
        }
    }

    private fun PaymentMethodDto.toDomainModel(): PaymentMethod {
        return when (this) {
            PaymentMethodDto.CASH -> PaymentMethod.CASH
            PaymentMethodDto.CARD -> PaymentMethod.CARD
            PaymentMethodDto.PREPAID -> PaymentMethod.PREPAID
        }
    }
}
