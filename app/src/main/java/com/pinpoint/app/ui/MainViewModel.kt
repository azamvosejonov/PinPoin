package com.pinpoint.app.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pinpoint.app.domain.model.Building
import com.pinpoint.app.domain.model.ThermalProjection
import com.pinpoint.app.domain.repository.BuildingRepository
import com.pinpoint.app.domain.repository.DeliverySessionRepository
import com.pinpoint.app.domain.repository.TrajectoryRepository
import com.pinpoint.app.domain.usecase.ComputeThermalProjectionUseCase
import com.pinpoint.app.domain.usecase.GenerateAlertsUseCase
import com.pinpoint.app.domain.usecase.GenerateThermalRouteAdviceUseCase
import com.pinpoint.app.domain.usecase.PredictivePinDropUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MainViewModel @Inject constructor(
    private val buildingRepository: BuildingRepository,
    private val trajectoryRepository: TrajectoryRepository,
    private val deliverySessionRepository: DeliverySessionRepository,
    private val computeThermalProjectionUseCase: ComputeThermalProjectionUseCase,
    private val generateThermalRouteAdviceUseCase: GenerateThermalRouteAdviceUseCase,
    private val generateAlertsUseCase: GenerateAlertsUseCase,
    private val predictivePinDropUseCase: PredictivePinDropUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(PinPoIntState())
    val uiState: StateFlow<PinPoIntState> = _uiState.asStateFlow()

    fun initialize() {
        // Fake data initialization for demo
        val building = Building(
            id = 1,
            externalId = "BUILDING123",
            address = "Tashkent, Chilanzar 13 kvartal",
            coordinate = com.pinpoint.app.domain.model.Coordinate(41.2995, 69.2401),
            buildingType = com.pinpoint.app.domain.model.BuildingType.NEW_TOWER,
            difficultyIndex = 4,
            hasLift = true,
            requiresChip = true,
            entranceHint = "Orqa tomondan kirish",
            entrances = emptyList(),
            updatedAt = System.currentTimeMillis()
        )
        val projection = computeThermalProjectionUseCase.compute(
            initialTemperature = 80.0,
            ambientTemperature = 5.0,
            insulationFactor = 0.6,
            totalMinutes = 18
        )
        val advice = generateThermalRouteAdviceUseCase.generateAdvice(building, projection)
        val alerts = generateAlertsUseCase.buildAlerts(building, projection)
        viewModelScope.launch {
            val adjustedCoordinate = predictivePinDropUseCase.adjustPin(
                rawCoordinate = building.coordinate,
                addressEmbedding = FloatArray(8) { index -> (index + 1) * 0.1f },
                historicalVector = FloatArray(8) { index -> (index + 1) * 0.05f }
            )
            _uiState.value = PinPoIntState(
                building = building,
                adjustedCoordinate = adjustedCoordinate,
                projection = projection,
                thermalAdvice = advice,
                alerts = alerts,
                domofonCode = "#3214"
            )
        }
    }

    fun onDelivered() {
        viewModelScope.launch {
            // Handle delivery logic
        }
    }

    fun onDomofonInfoRequested() {
        // Show bottom sheet or overlay
    }

    fun onCopyDomofonCode() {
        // Handle copy to clipboard
    }

    fun onCallClient() {
        // Show call intent
    }
}
