package com.pinpoint.app.service

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import androidx.lifecycle.LifecycleService
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow

@AndroidEntryPoint
class ActivityRecognitionService : Service() {

    private val _transportModeFlow = MutableSharedFlow<String>(replay = 1)
    val transportModeFlow = _transportModeFlow.asSharedFlow()

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val result = com.google.android.gms.location.ActivityTransitionResult.extractResult(intent)
        result?.transitionEvents?.forEach { event ->
            val mode = when (event.activityType) {
                com.google.android.gms.location.DetectedActivity.IN_VEHICLE -> "VEHICLE"
                com.google.android.gms.location.DetectedActivity.ON_BICYCLE -> "BICYCLE"
                com.google.android.gms.location.DetectedActivity.ON_FOOT,
                com.google.android.gms.location.DetectedActivity.STILL -> "FOOT"
                else -> "UNKNOWN"
            }
            Log.d("ActivityRecognition", "Detected activity: $mode")
            _transportModeFlow.tryEmit(mode)
        }
        return START_NOT_STICKY
    }
}
