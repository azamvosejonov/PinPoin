package com.pinpoint.app.util

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import androidx.core.app.NotificationCompat
import com.pinpoint.app.R

object NotificationHelper {
    const val CHANNEL_LOCATION = "pinpoint_location_channel"
    const val CHANNEL_ALERT = "pinpoint_alert_channel"
    const val NOTIFICATION_ID_TRACKING = 1001

    fun ensureChannels(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val locationChannel = NotificationChannel(
                CHANNEL_LOCATION,
                context.getString(R.string.notification_channel_location),
                NotificationManager.IMPORTANCE_LOW
            )
            val alertChannel = NotificationChannel(
                CHANNEL_ALERT,
                context.getString(R.string.notification_channel_alerts),
                NotificationManager.IMPORTANCE_HIGH
            )
            manager.createNotificationChannel(locationChannel)
            manager.createNotificationChannel(alertChannel)
        }
    }

    fun buildTrackingNotification(context: Context): Notification {
        return NotificationCompat.Builder(context, CHANNEL_LOCATION)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(context.getString(R.string.notification_tracking_title))
            .setContentText(context.getString(R.string.notification_tracking_text))
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    fun buildAlertNotification(context: Context, title: String, message: String): Notification {
        return NotificationCompat.Builder(context, CHANNEL_ALERT)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()
    }
}
