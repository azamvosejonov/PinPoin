package com.pinpoint.app.data.remote.geocoding

import com.pinpoint.app.domain.model.Coordinate
import javax.inject.Inject

class GeocodingRemoteDataSource @Inject constructor(
    private val api: NominatimApi
) {

    suspend fun geocodeAddress(address: String): Coordinate? {
        val results = api.search(address)
        val best = results.firstOrNull()
        return best?.let {
            Coordinate(it.lat.toDouble(), it.lon.toDouble())
        }
    }

    suspend fun reverseGeocode(lat: Double, lon: Double): String? {
        return api.reverse(lat, lon)?.displayName
    }
}
