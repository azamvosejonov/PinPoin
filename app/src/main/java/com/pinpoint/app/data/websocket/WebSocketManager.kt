package com.pinpoint.app.data.websocket

import android.util.Log
import com.google.gson.Gson
import com.google.gson.JsonObject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class WebSocketManager @Inject constructor(
    private val okHttpClient: OkHttpClient,
    private val gson: Gson
) {
    private var webSocket: WebSocket? = null
    private val isConnected = MutableStateFlow(false)
    private val _messages = MutableStateFlow<String?>(null)
    
    val connectionState: StateFlow<Boolean> = isConnected.asStateFlow()
    val messages: StateFlow<String?> = _messages.asStateFlow()

    private val listener = object : WebSocketListener() {
        override fun onOpen(webSocket: WebSocket, response: Response) {
            Log.d("WebSocket", "Connected")
            isConnected.value = true
        }

        override fun onMessage(webSocket: WebSocket, text: String) {
            Log.d("WebSocket", "Message: $text")
            _messages.value = text
        }

        override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
            Log.d("WebSocket", "Closing: $code $reason")
            isConnected.value = false
        }

        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            Log.e("WebSocket", "Error", t)
            isConnected.value = false
        }
    }

    fun connect(url: String, token: String) {
        val request = Request.Builder()
            .url(url)
            .addHeader("Authorization", "Bearer $token")
            .build()
        
        webSocket = okHttpClient.newWebSocket(request, listener)
    }

    fun disconnect() {
        webSocket?.close(1000, "User disconnected")
        webSocket = null
        isConnected.value = false
    }

    fun sendMessage(message: JsonObject) {
        webSocket?.send(gson.toJson(message))
    }

    fun sendLocationUpdate(latitude: Double, longitude: Double) {
        val message = JsonObject().apply {
            addProperty("type", "location_update")
            addProperty("latitude", latitude)
            addProperty("longitude", longitude)
            addProperty("timestamp", System.currentTimeMillis())
        }
        sendMessage(message)
    }

    fun sendOrderStatusUpdate(orderId: Int, status: String) {
        val message = JsonObject().apply {
            addProperty("type", "order_status_update")
            addProperty("order_id", orderId)
            addProperty("status", status)
            addProperty("timestamp", System.currentTimeMillis())
        }
        sendMessage(message)
    }

    fun sendCourierStatusUpdate(status: String) {
        val message = JsonObject().apply {
            addProperty("type", "courier_status_update")
            addProperty("status", status)
            addProperty("timestamp", System.currentTimeMillis())
        }
        sendMessage(message)
    }
}
