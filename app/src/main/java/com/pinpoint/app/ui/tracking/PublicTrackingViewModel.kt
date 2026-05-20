package com.pinpoint.app.ui.tracking

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pinpoint.app.domain.model.OrderTracking
import com.pinpoint.app.domain.repository.BackendRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class PublicTrackingViewModel @Inject constructor(
    private val backendRepository: BackendRepository
) : ViewModel() {

    private val _orderTracking = MutableStateFlow<OrderTracking?>(null)
    val orderTracking: StateFlow<OrderTracking?> = _orderTracking.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    fun trackOrder(trackingHash: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            backendRepository.getPublicTracking(trackingHash)
                .onSuccess { tracking ->
                    _orderTracking.value = tracking
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Buyurtmani kuzatishda xatolik"
                }
            _isLoading.value = false
        }
    }

    fun clearError() {
        _error.value = null
    }
}
