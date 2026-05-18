package com.pinpoint.app.di

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.pinpoint.app.BuildConfig
import com.pinpoint.app.data.remote.backend.BackendApi
import com.pinpoint.app.data.remote.backend.BackendRemoteDataSource
import com.pinpoint.app.data.remote.geocoding.GeocodingRemoteDataSource
import com.pinpoint.app.data.remote.geocoding.NominatimApi
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideGson(): Gson = GsonBuilder().create()

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        return OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(logging)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient, gson: Gson): Retrofit = Retrofit.Builder()
        .baseUrl("https://nominatim.openstreetmap.org")
        .client(client)
        .addConverterFactory(GsonConverterFactory.create(gson))
        .build()

    @Provides
    @Singleton
    fun provideNominatimApi(retrofit: Retrofit): NominatimApi = retrofit.create(NominatimApi::class.java)

    @Provides
    @Singleton
    fun provideGeocodingRemoteDataSource(api: NominatimApi): GeocodingRemoteDataSource = GeocodingRemoteDataSource(api)

    @Provides
    @Singleton
    fun provideBackendApi(client: OkHttpClient, gson: Gson): BackendApi = Retrofit.Builder()
        .baseUrl(BuildConfig.BACKEND_BASE_URL)
        .client(client)
        .addConverterFactory(GsonConverterFactory.create(gson))
        .build()
        .create(BackendApi::class.java)

    @Provides
    @Singleton
    fun provideBackendRemoteDataSource(api: BackendApi): BackendRemoteDataSource = BackendRemoteDataSource(api)
}
