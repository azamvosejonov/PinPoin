package com.pinpoint.app.ui.restaurant

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pinpoint.app.domain.model.Restaurant
import com.pinpoint.app.domain.repository.BackendRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class RestaurantViewModel @Inject constructor(
    private val backendRepository: BackendRepository
) : ViewModel() {

    private val _restaurants = MutableStateFlow<List<Restaurant>>(emptyList())
    val restaurants: StateFlow<List<Restaurant>> = _restaurants.asStateFlow()

    private val _selectedRestaurant = MutableStateFlow<Restaurant?>(null)
    val selectedRestaurant: StateFlow<Restaurant?> = _selectedRestaurant.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    init {
        loadRestaurants()
    }

    fun loadRestaurants() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            backendRepository.getRestaurants()
                .onSuccess { restaurants ->
                    _restaurants.value = restaurants
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Restoranlarni yuklashda xatolik"
                }
            _isLoading.value = false
        }
    }

    fun loadRestaurant(restaurantId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            backendRepository.getRestaurant(restaurantId)
                .onSuccess { restaurant ->
                    _selectedRestaurant.value = restaurant
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Restoranni yuklashda xatolik"
                }
            _isLoading.value = false
        }
    }

    fun selectRestaurant(restaurant: Restaurant) {
        _selectedRestaurant.value = restaurant
    }

    fun clearError() {
        _error.value = null
    }
}
