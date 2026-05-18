package com.pinpoint.app.data.local

import androidx.room.TypeConverter
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.pinpoint.app.domain.model.LocationPoint

class PointListConverter {

    private val gson = Gson()
    private val typeToken = object : TypeToken<List<LocationPoint>>() {}.type

    @TypeConverter
    fun fromList(points: List<LocationPoint>?): String? {
        return points?.let { gson.toJson(it, typeToken) }
    }

    @TypeConverter
    fun toList(json: String?): List<LocationPoint>? {
        return json?.let { gson.fromJson<List<LocationPoint>>(it, typeToken) }
    }
}
