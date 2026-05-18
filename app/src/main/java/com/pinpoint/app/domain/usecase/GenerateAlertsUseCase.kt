package com.pinpoint.app.domain.usecase

import com.pinpoint.app.domain.model.Building
import com.pinpoint.app.domain.model.ThermalProjection
import javax.inject.Inject

class GenerateAlertsUseCase @Inject constructor() {

    fun buildAlerts(building: Building, projection: ThermalProjection): List<String> {
        val alerts = mutableListOf<String>()
        if (building.requiresChip) {
            alerts.add("Diqqat! Ushbu binoda lift faqat chip bilan ishlaydi. Mijozga hoziroq qo'ng'iroq qilib, pastga tushishini so'rang")
        }
        if (building.entranceHint?.contains("orqa", true) == true) {
            alerts.add("Podyezdga kirish faqat orqa hovli orqali")
        }
        if (projection.riskLevel == com.pinpoint.app.domain.model.ThermalRiskLevel.HIGH) {
            alerts.add("Tezroq harakat qiling, taom sovush arafasida!")
        }
        return alerts
    }
}
