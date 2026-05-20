package com.pinpoint.app.ui.indoor

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pinpoint.app.data.remote.backend.dto.TelemetryDto
import com.pinpoint.app.data.remote.backend.dto.IndoorTelemetryPointDto
import com.pinpoint.app.domain.model.IndoorMap
import com.pinpoint.app.domain.model.IndoorPathCreate
import com.pinpoint.app.domain.model.IndoorPathDetail
import com.pinpoint.app.domain.model.IsometricTile
import com.pinpoint.app.domain.model.TileType
import com.pinpoint.app.domain.repository.BackendRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class IndoorMapViewModel @Inject constructor(
    private val backendRepository: BackendRepository
) : ViewModel() {

    private val _indoorMap = MutableStateFlow<IndoorMap?>(null)
    val indoorMap: StateFlow<IndoorMap?> = _indoorMap.asStateFlow()

    private val _indoorPaths = MutableStateFlow<List<IndoorPathDetail>>(emptyList())
    val indoorPaths: StateFlow<List<IndoorPathDetail>> = _indoorPaths.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    private val _isIndoorMode = MutableStateFlow(false)
    val isIndoorMode: StateFlow<Boolean> = _isIndoorMode.asStateFlow()

    private val _floorTiles = MutableStateFlow<List<IsometricTile>>(emptyList())
    val floorTiles: StateFlow<List<IsometricTile>> = _floorTiles.asStateFlow()

    private val _courierTilePosition = MutableStateFlow<Pair<Int, Int>?>(null)
    val courierTilePosition: StateFlow<Pair<Int, Int>?> = _courierTilePosition.asStateFlow()

    fun loadIndoorMap(externalId: String, entrance: Int = 1, floor: Int = 1) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            backendRepository.getIndoorMap(externalId, entrance, floor)
                .onSuccess { map ->
                    _indoorMap.value = map
                    generateIsometricTiles(map)
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Ichki xaritani olishda xatolik"
                }
            _isLoading.value = false
        }
    }

    fun createIndoorPath(externalId: String, path: IndoorPathCreate) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            backendRepository.createIndoorPath(externalId, path)
                .onSuccess { newPath ->
                    _indoorPaths.value = _indoorPaths.value + newPath
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Yo'l yaratishda xatolik"
                }
            _isLoading.value = false
        }
    }

    fun submitTelemetry(
        externalId: String,
        orderId: Int,
        courierId: Int,
        entrance: Int,
        floor: Int,
        trajectory: List<IndoorTelemetryPointDto>
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            val telemetry = TelemetryDto(
                orderId = orderId,
                courierId = courierId,
                entrance = entrance,
                floor = floor,
                trajectory = trajectory,
                timestamp = System.currentTimeMillis()
            )
            backendRepository.submitTelemetry(externalId, telemetry)
                .onSuccess {
                    // Telemetry submitted successfully
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Telemetriya yuborishda xatolik"
                }
            _isLoading.value = false
        }
    }

    fun checkGeofence(courierLat: Double, courierLon: Double, buildingLat: Double, buildingLon: Double) {
        val distanceMeters = haversineMeters(courierLat, courierLon, buildingLat, buildingLon)
        val wasIndoor = _isIndoorMode.value
        _isIndoorMode.value = distanceMeters <= 50.0
        if (!wasIndoor && _isIndoorMode.value) {
            _indoorMap.value?.let { map ->
                loadIndoorMap(map.buildingExternalId, map.entrance, map.floorNumber)
            }
        }
    }

    fun updateCourierPosition(tileX: Int, tileY: Int) {
        _courierTilePosition.value = Pair(tileX, tileY)
    }

    private fun generateIsometricTiles(map: IndoorMap) {
        val w = map.width ?: 10
        val h = map.height ?: 10
        val tiles = mutableListOf<IsometricTile>()
        for (y in 0 until h) {
            for (x in 0 until w) {
                val type = when {
                    x == 0 || x == w - 1 || y == 0 || y == h - 1 -> TileType.WALL
                    map.route?.pathPoints?.any { it.x.toInt() == x && it.y.toInt() == y } == true -> TileType.HIGHLIGHT_PATH
                    else -> TileType.FLOOR
                }
                val label = when (type) {
                    TileType.HIGHLIGHT_PATH -> map.route?.pathPoints?.find { it.x.toInt() == x && it.y.toInt() == y }?.label
                    else -> null
                }
                tiles.add(IsometricTile(x, y, type, label))
            }
        }
        map.route?.startPoint?.let { start ->
            tiles.add(IsometricTile(start.x.toInt(), start.y.toInt(), TileType.DOOR, "Kirish"))
        }
        map.route?.endPoint?.let { end ->
            tiles.add(IsometricTile(end.x.toInt(), end.y.toInt(), TileType.APARTMENT, "Xonadon"))
        }
        _floorTiles.value = tiles
    }

    private fun haversineMeters(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val r = 6371000.0
        val dLat = Math.toRadians(lat2 - lat1)
        val dLon = Math.toRadians(lon2 - lon1)
        val a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2)
        val c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
        return r * c
    }

    fun clearError() {
        _error.value = null
    }
}
