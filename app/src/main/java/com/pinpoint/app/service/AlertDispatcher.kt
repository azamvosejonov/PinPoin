package com.pinpoint.app.service

import android.content.Context
import android.media.AudioManager
import android.media.ToneGenerator
import com.pinpoint.app.util.NotificationHelper
import com.pinpoint.app.util.SpeechHelper
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AlertDispatcher @Inject constructor(
    @ApplicationContext private val context: Context
) {

    fun dispatchAlert(message: String) {
        val notification = NotificationHelper.buildAlertNotification(context, "PinPoInt", message)
        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as android.app.NotificationManager
        manager.notify((Math.random() * 10000).toInt(), notification)
        SpeechHelper.speak(context, message)
        beep()
    }

    private fun beep() {
        val tone = ToneGenerator(AudioManager.STREAM_ALARM, 80)
        tone.startTone(ToneGenerator.TONE_PROP_BEEP2, 500)
    }
}
