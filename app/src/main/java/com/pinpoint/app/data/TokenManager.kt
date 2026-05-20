package com.pinpoint.app.data

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

class TokenManager(private val context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val sharedPreferences: SharedPreferences by lazy {
        EncryptedSharedPreferences.create(
            context,
            "secure_tokens",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    private val _accessToken = MutableStateFlow<String?>(null)
    val accessToken: Flow<String?> = _accessToken.asStateFlow()

    private val _refreshToken = MutableStateFlow<String?>(null)
    val refreshToken: Flow<String?> = _refreshToken.asStateFlow()

    init {
        loadTokens()
    }

    private fun loadTokens() {
        _accessToken.value = sharedPreferences.getString("access_token", null)
        _refreshToken.value = sharedPreferences.getString("refresh_token", null)
    }

    fun saveTokens(accessToken: String, refreshToken: String) {
        sharedPreferences.edit()
            .putString("access_token", accessToken)
            .putString("refresh_token", refreshToken)
            .apply()
        _accessToken.value = accessToken
        _refreshToken.value = refreshToken
    }

    fun clearTokens() {
        sharedPreferences.edit()
            .remove("access_token")
            .remove("refresh_token")
            .apply()
        _accessToken.value = null
        _refreshToken.value = null
    }
}
