package com.pinpoint.app.di

import android.content.Context
import androidx.room.Room
import com.pinpoint.app.data.local.PinPoIntDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): PinPoIntDatabase = Room.databaseBuilder(
        context,
        PinPoIntDatabase::class.java,
        "pinpoint.db"
    ).fallbackToDestructiveMigration()
        .build()

    @Provides
    fun provideBuildingDao(database: PinPoIntDatabase) = database.buildingDao()

    @Provides
    fun provideTrajectoryDao(database: PinPoIntDatabase) = database.trajectoryDao()

    @Provides
    fun provideDeliverySessionDao(database: PinPoIntDatabase) = database.deliverySessionDao()
}
