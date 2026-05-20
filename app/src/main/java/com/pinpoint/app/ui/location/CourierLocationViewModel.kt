package com.pinpoint.app.ui.location

import android.Manifest
import android.content.pm.PackageManager
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import com.google.android.gms.location.Priority
import com.pinpoint.app.data.websocket.WebSocketManager
import com.pinpoint.app.domain.model.CourierLocation
import com.pinpoint.app.domain.repository.BackendRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class CourierLocationViewModel @Inject constructor(
    private val backendRepository: BackendRepository,
    private val webSocketManager: WebSocketManager,
    private val fusedLocationClient: FusedLocationProviderClient
) : ViewModel() {

    private val _courierLocation = MutableStateFlow<CourierLocation?>(null)
    val courierLocation: StateFlow<CourierLocation?> = _courierLocation.asStateFlow()

    private val _currentLocation = MutableStateFlow<Pair<Double, Double>?>(null)
    val currentLocation: StateFlow<Pair<Double, Double>?> = _currentLocation.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    private val _isTracking = MutableStateFlow(false)
    val isTracking: StateFlow<Boolean> = _isTracking.asStateFlow()

    private val locationCallback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            result.lastLocation?.let { location ->
                _currentLocation.value = Pair(location.latitude, location.longitude)
                // Send real-time location update via WebSocket
                webSocketManager.sendLocationUpdate(location.latitude, location.longitude)
            }
        }
    }

    init {
        loadCourierLocation()
    }

    fun loadCourierLocation(courierId: Int = 1) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            backendRepository.getCourierLocation(courierId)
                .onSuccess { location ->
                    _courierLocation.value = location
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Joylashuvni olishda xatolik"
                }
            _isLoading.value = false
        }
    }

    fun startRealtimeTracking() {
        if (_isTracking.value) return

        val locationRequest = LocationRequest.Builder(
            Priority.PRIORITY_HIGH_ACCURACY, 5000 // Update every 5 seconds
        ).apply {
            setMinUpdateDistanceMeters(10f)
        }.build()

        try {
            fusedLocationClient.requestLocationUpdates(
                locationRequest,
                locationCallback,
                null
            )
            _isTracking.value = true
        } catch (e: SecurityException) {
            _error.value = "Location permission denied"
        }
    }

    fun stopRealtimeTracking() {
        if (!_isTracking.value) return
        
        fusedLocationClient.removeLocationUpdates(locationCallback)
        _isTracking.value = false
    }

    fun updateLocation(latitude: Double, longitude: Double) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            backendRepository.updateLocation(latitude, longitude)
                .onSuccess { location ->
                    _courierLocation.value = location
                    webSocketManager.sendLocationUpdate(latitude, longitude)
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Joylashuvni yangilashda xatolik"
                }
            _isLoading.value = false
        }
    }

    fun clearError() {
        _error.value = null
    }

    override fun onCleared() {
        super.onCleared()
        stopRealtimeTracking()
    }
}
