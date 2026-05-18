package com.pinpoint.app.util

import android.content.Context
import android.speech.tts.TextToSpeech
import java.util.Locale

object SpeechHelper {

    private var tts: TextToSpeech? = null

    fun speak(context: Context, message: String) {
        val engine = tts ?: TextToSpeech(context.applicationContext) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale("uz")
            }
        }.also { tts = it }
        engine.language = Locale("uz")
        engine.speak(message, TextToSpeech.QUEUE_ADD, null, System.currentTimeMillis().toString())
    }

    fun shutdown() {
        tts?.shutdown()
        tts = null
    }
}
