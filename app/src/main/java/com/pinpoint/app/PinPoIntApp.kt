package com.pinpoint.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel

@HiltAndroidApp
class PinPoIntApp : Application() {
    val applicationScope = CoroutineScope(SupervisorJob())

    override fun onTerminate() {
        super.onTerminate()
        applicationScope.cancel()
    }
}
