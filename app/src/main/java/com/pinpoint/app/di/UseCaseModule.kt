package com.pinpoint.app.di

import com.pinpoint.app.domain.usecase.AnalyzeTrajectoryUseCase
import com.pinpoint.app.domain.usecase.ComputeBuildingDifficultyUseCase
import com.pinpoint.app.domain.usecase.ComputeThermalProjectionUseCase
import com.pinpoint.app.domain.usecase.GenerateAlertsUseCase
import com.pinpoint.app.domain.usecase.GenerateThermalRouteAdviceUseCase
import com.pinpoint.app.domain.usecase.IdentifyEntranceFromTrajectoriesUseCase
import com.pinpoint.app.domain.usecase.OfflineSyncUseCase
import com.pinpoint.app.domain.usecase.PredictivePinDropUseCase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object UseCaseModule {

    @Provides
    @Singleton
    fun provideComputeBuildingDifficultyUseCase() = ComputeBuildingDifficultyUseCase()

    @Provides
    @Singleton
    fun provideIdentifyEntranceUseCase() = IdentifyEntranceFromTrajectoriesUseCase()

    @Provides
    @Singleton
    fun provideComputeThermalProjectionUseCase() = ComputeThermalProjectionUseCase()

    @Provides
    @Singleton
    fun provideGenerateThermalRouteAdviceUseCase(
        computeBuildingDifficultyUseCase: ComputeBuildingDifficultyUseCase
    ) = GenerateThermalRouteAdviceUseCase(computeBuildingDifficultyUseCase)

    @Provides
    @Singleton
    fun provideGenerateAlertsUseCase() = GenerateAlertsUseCase()

    @Provides
    @Singleton
    fun providePredictivePinDropUseCase() = PredictivePinDropUseCase(com.pinpoint.app.data.remote.predictive.PinCorrectionModel())
}
