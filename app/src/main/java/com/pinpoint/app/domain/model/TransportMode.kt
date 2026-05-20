package com.pinpoint.app.domain.model

enum class TransportMode(val apiValue: String) {
    VEHICLE("car"),
    BICYCLE("bicycle"),
    FOOT("pedestrian"),
    UNKNOWN("pedestrian");

    companion object {
        fun fromApiValue(value: String?): TransportMode {
            return entries.find { it.apiValue == value } ?: UNKNOWN
        }
    }
}
