package com.pinpoint.app.di

import com.pinpoint.app.data.repository.BuildingRepositoryImpl
import com.pinpoint.app.data.repository.DeliverySessionRepositoryImpl
import com.pinpoint.app.data.repository.TrajectoryRepositoryImpl
import com.pinpoint.app.data.repository.OrderRepositoryImpl
import com.pinpoint.app.data.repository.BackendRepositoryImpl
import com.pinpoint.app.domain.repository.BuildingRepository
import com.pinpoint.app.domain.repository.DeliverySessionRepository
import com.pinpoint.app.domain.repository.TrajectoryRepository
import com.pinpoint.app.domain.repository.OrderRepository
import com.pinpoint.app.domain.repository.BackendRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindBuildingRepository(impl: BuildingRepositoryImpl): BuildingRepository

    @Binds
    @Singleton
    abstract fun bindTrajectoryRepository(impl: TrajectoryRepositoryImpl): TrajectoryRepository

    @Binds
    @Singleton
    abstract fun bindDeliverySessionRepository(impl: DeliverySessionRepositoryImpl): DeliverySessionRepository

    @Binds
    @Singleton
    abstract fun bindOrderRepository(impl: OrderRepositoryImpl): OrderRepository

    @Binds
    @Singleton
    abstract fun bindBackendRepository(impl: BackendRepositoryImpl): BackendRepository
}
