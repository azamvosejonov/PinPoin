package com.pinpoint.app.ui.order

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pinpoint.app.domain.model.Order
import com.pinpoint.app.domain.model.OrderStatus
import com.pinpoint.app.domain.model.CourierStatus
import com.pinpoint.app.domain.model.CourierStatusEnum
import com.pinpoint.app.domain.repository.OrderRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class OrderViewModel @Inject constructor(
    private val orderRepository: OrderRepository
) : ViewModel() {

    private val _orders = MutableStateFlow<List<Order>>(emptyList())
    val orders: StateFlow<List<Order>> = _orders.asStateFlow()

    private val _selectedOrder = MutableStateFlow<Order?>(null)
    val selectedOrder: StateFlow<Order?> = _selectedOrder.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    private val _courierStatus = MutableStateFlow<CourierStatus?>(null)
    val courierStatus: StateFlow<CourierStatus?> = _courierStatus.asStateFlow()

    init {
        loadOrders()
        loadCourierStatus()
    }

    fun loadOrders() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            orderRepository.getMyOrders()
                .onSuccess { orders ->
                    _orders.value = orders
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Xatolik yuz berdi"
                }
            _isLoading.value = false
        }
    }

    fun loadOrder(orderId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            orderRepository.getOrder(orderId)
                .onSuccess { order ->
                    _selectedOrder.value = order
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Xatolik yuz berdi"
                }
            _isLoading.value = false
        }
    }

    fun updateOrderStatus(orderId: Int, status: OrderStatus) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            orderRepository.updateOrderStatus(orderId, status)
                .onSuccess { order ->
                    _selectedOrder.value = order
                    loadOrders() // Refresh list
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Xatolik yuz berdi"
                }
            _isLoading.value = false
        }
    }

    fun declineOrder(orderId: Int, reason: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            orderRepository.declineOrder(orderId, reason)
                .onSuccess { order ->
                    _selectedOrder.value = order
                    loadOrders() // Refresh list
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Xatolik yuz berdi"
                }
            _isLoading.value = false
        }
    }

    fun loadCourierStatus() {
        viewModelScope.launch {
            _error.value = null
            // Assuming courier ID is stored somewhere, for now using a default
            orderRepository.getCourierStatus(1)
                .onSuccess { status ->
                    _courierStatus.value = status
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Xatolik yuz berdi"
                }
        }
    }

    fun updateCourierStatus(status: CourierStatusEnum) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            orderRepository.updateCourierStatus(status)
                .onSuccess { courierStatus ->
                    _courierStatus.value = courierStatus
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Xatolik yuz berdi"
                }
            _isLoading.value = false
        }
    }

    fun collectCash(courierId: Int, amount: Double) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            orderRepository.collectCash(courierId, amount)
                .onSuccess { courierStatus ->
                    _courierStatus.value = courierStatus
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Xatolik yuz berdi"
                }
            _isLoading.value = false
        }
    }

    fun selectOrder(order: Order) {
        _selectedOrder.value = order
    }

    fun clearError() {
        _error.value = null
    }
}
