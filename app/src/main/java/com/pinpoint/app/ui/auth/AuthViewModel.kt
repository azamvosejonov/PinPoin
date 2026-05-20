package com.pinpoint.app.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pinpoint.app.data.TokenManager
import com.pinpoint.app.domain.model.User
import com.pinpoint.app.domain.model.TokenPair
import com.pinpoint.app.domain.repository.BackendRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val backendRepository: BackendRepository,
    private val tokenManager: TokenManager
) : ViewModel() {

    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    init {
        checkLoginStatus()
    }

    private fun checkLoginStatus() {
        viewModelScope.launch {
            val accessToken = tokenManager.accessToken.first()
            if (accessToken != null) {
                _isLoggedIn.value = true
                getMe()
            }
        }
    }

    fun register(email: String, password: String, fullName: String?, phone: String?, role: String?) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            backendRepository.register(email, password, fullName, phone, role)
                .onSuccess { user ->
                    _user.value = user
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Ro'yxatdan o'tishda xatolik"
                }
            _isLoading.value = false
        }
    }

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            backendRepository.login(email, password)
                .onSuccess { tokenPair ->
                    tokenManager.saveTokens(tokenPair.accessToken, tokenPair.refreshToken)
                    _isLoggedIn.value = true
                    getMe()
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Login xatolik"
                }
            _isLoading.value = false
        }
    }

    fun getMe() {
        viewModelScope.launch {
            _error.value = null
            backendRepository.getMe()
                .onSuccess { user ->
                    _user.value = user
                }
                .onFailure { e ->
                    _error.value = e.message ?: "Foydalanuvchi ma'lumotlarini olishda xatolik"
                }
        }
    }

    fun logout() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            val accessToken = tokenManager.accessToken.first()
            val refreshToken = tokenManager.refreshToken.first()
            if (accessToken != null && refreshToken != null) {
                backendRepository.logout(accessToken, refreshToken)
                    .onSuccess {
                        tokenManager.clearTokens()
                        _isLoggedIn.value = false
                        _user.value = null
                    }
                    .onFailure { e ->
                        _error.value = e.message ?: "Logout xatolik"
                    }
            } else {
                tokenManager.clearTokens()
                _isLoggedIn.value = false
                _user.value = null
            }
            _isLoading.value = false
        }
    }

    fun clearError() {
        _error.value = null
    }
}
