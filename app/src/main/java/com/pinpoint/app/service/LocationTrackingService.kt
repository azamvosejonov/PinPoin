package com.pinpoint.app.service

import android.Manifest
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.location.Location
import android.os.IBinder
import androidx.core.content.ContextCompat
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import com.google.android.gms.location.LocationServices
import com.pinpoint.app.util.NotificationHelper
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.cancel
import javax.inject.Inject

@AndroidEntryPoint
class LocationTrackingService : Service() {

    @Inject
    lateinit var activityRecognitionManager: TransportActivityManager

    @Inject
    lateinit var trajectoryRecorder: TrajectoryRecorder

    private val fusedLocationClient by lazy { LocationServices.getFusedLocationProviderClient(this) }
    private val scope = CoroutineScope(Dispatchers.IO + Job())

    private val locationFlow = MutableSharedFlow<Location>(replay = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)

    private val locationCallback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            result.lastLocation?.let { location ->
                scope.launch {
                    locationFlow.emit(location)
                }
                trajectoryRecorder.recordLocation(location)
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        NotificationHelper.ensureChannels(this)
        startForeground(
            NotificationHelper.NOTIFICATION_ID_TRACKING,
            NotificationHelper.buildTrackingNotification(this)
        )
        activityRecognitionManager.startRecognition()
        requestLocationUpdates()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        fusedLocationClient.removeLocationUpdates(locationCallback)
        activityRecognitionManager.stopRecognition()
        scope.cancel()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun requestLocationUpdates() {
        val hasFine = ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        if (!hasFine) return

        val request = LocationRequest.Builder(2000).apply {
            setMinUpdateIntervalMillis(1000)
            setMinUpdateDistanceMeters(3f)
        }.build()

        fusedLocationClient.requestLocationUpdates(request, locationCallback, mainLooper)
    }
}
