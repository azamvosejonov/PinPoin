package com.pinpoint.app.domain.repository

import com.pinpoint.app.domain.model.Order
import com.pinpoint.app.domain.model.CourierStatus
import com.pinpoint.app.domain.model.OrderStatus
import com.pinpoint.app.domain.model.CourierStatusEnum
import com.pinpoint.app.domain.model.PaymentMethod

interface OrderRepository {
    suspend fun getMyOrders(): Result<List<Order>>
    suspend fun getOrder(orderId: Int): Result<Order>
    suspend fun updateOrderStatus(orderId: Int, status: OrderStatus): Result<Order>
    suspend fun declineOrder(orderId: Int, reason: String): Result<Order>
    suspend fun updateCourierStatus(status: CourierStatusEnum): Result<CourierStatus>
    suspend fun getCourierStatus(courierId: Int): Result<CourierStatus>
    suspend fun collectCash(courierId: Int, amount: Double): Result<CourierStatus>
}
