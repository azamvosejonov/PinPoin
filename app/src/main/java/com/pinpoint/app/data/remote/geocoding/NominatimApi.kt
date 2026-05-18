package com.pinpoint.app.data.remote.geocoding

import retrofit2.http.GET
import retrofit2.http.Query

interface NominatimApi {

    @GET("/search")
    suspend fun search(
        @Query("q") query: String,
        @Query("format") format: String = "jsonv2",
        @Query("limit") limit: Int = 3
    ): List<NominatimResponse>

    @GET("/reverse")
    suspend fun reverse(
        @Query("lat") lat: Double,
        @Query("lon") lon: Double,
        @Query("format") format: String = "jsonv2"
    ): NominatimResponse?
}
