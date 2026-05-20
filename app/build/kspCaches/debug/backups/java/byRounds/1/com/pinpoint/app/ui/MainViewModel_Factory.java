package com.pinpoint.app.ui;

import com.pinpoint.app.domain.repository.BuildingRepository;
import com.pinpoint.app.domain.repository.DeliverySessionRepository;
import com.pinpoint.app.domain.repository.TrajectoryRepository;
import com.pinpoint.app.domain.usecase.ComputeThermalProjectionUseCase;
import com.pinpoint.app.domain.usecase.GenerateAlertsUseCase;
import com.pinpoint.app.domain.usecase.GenerateThermalRouteAdviceUseCase;
import com.pinpoint.app.domain.usecase.PredictivePinDropUseCase;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata
@QualifierMetadata
@DaggerGenerated
@Generated(
    value = "dagger.internal.codegen.ComponentProcessor",
    comments = "https://dagger.dev"
)
@SuppressWarnings({
    "unchecked",
    "rawtypes",
    "KotlinInternal",
    "KotlinInternalInJava"
})
public final class MainViewModel_Factory implements Factory<MainViewModel> {
  private final Provider<BuildingRepository> buildingRepositoryProvider;

  private final Provider<TrajectoryRepository> trajectoryRepositoryProvider;

  private final Provider<DeliverySessionRepository> deliverySessionRepositoryProvider;

  private final Provider<ComputeThermalProjectionUseCase> computeThermalProjectionUseCaseProvider;

  private final Provider<GenerateThermalRouteAdviceUseCase> generateThermalRouteAdviceUseCaseProvider;

  private final Provider<GenerateAlertsUseCase> generateAlertsUseCaseProvider;

  private final Provider<PredictivePinDropUseCase> predictivePinDropUseCaseProvider;

  public MainViewModel_Factory(Provider<BuildingRepository> buildingRepositoryProvider,
      Provider<TrajectoryRepository> trajectoryRepositoryProvider,
      Provider<DeliverySessionRepository> deliverySessionRepositoryProvider,
      Provider<ComputeThermalProjectionUseCase> computeThermalProjectionUseCaseProvider,
      Provider<GenerateThermalRouteAdviceUseCase> generateThermalRouteAdviceUseCaseProvider,
      Provider<GenerateAlertsUseCase> generateAlertsUseCaseProvider,
      Provider<PredictivePinDropUseCase> predictivePinDropUseCaseProvider) {
    this.buildingRepositoryProvider = buildingRepositoryProvider;
    this.trajectoryRepositoryProvider = trajectoryRepositoryProvider;
    this.deliverySessionRepositoryProvider = deliverySessionRepositoryProvider;
    this.computeThermalProjectionUseCaseProvider = computeThermalProjectionUseCaseProvider;
    this.generateThermalRouteAdviceUseCaseProvider = generateThermalRouteAdviceUseCaseProvider;
    this.generateAlertsUseCaseProvider = generateAlertsUseCaseProvider;
    this.predictivePinDropUseCaseProvider = predictivePinDropUseCaseProvider;
  }

  @Override
  public MainViewModel get() {
    return newInstance(buildingRepositoryProvider.get(), trajectoryRepositoryProvider.get(), deliverySessionRepositoryProvider.get(), computeThermalProjectionUseCaseProvider.get(), generateThermalRouteAdviceUseCaseProvider.get(), generateAlertsUseCaseProvider.get(), predictivePinDropUseCaseProvider.get());
  }

  public static MainViewModel_Factory create(
      Provider<BuildingRepository> buildingRepositoryProvider,
      Provider<TrajectoryRepository> trajectoryRepositoryProvider,
      Provider<DeliverySessionRepository> deliverySessionRepositoryProvider,
      Provider<ComputeThermalProjectionUseCase> computeThermalProjectionUseCaseProvider,
      Provider<GenerateThermalRouteAdviceUseCase> generateThermalRouteAdviceUseCaseProvider,
      Provider<GenerateAlertsUseCase> generateAlertsUseCaseProvider,
      Provider<PredictivePinDropUseCase> predictivePinDropUseCaseProvider) {
    return new MainViewModel_Factory(buildingRepositoryProvider, trajectoryRepositoryProvider, deliverySessionRepositoryProvider, computeThermalProjectionUseCaseProvider, generateThermalRouteAdviceUseCaseProvider, generateAlertsUseCaseProvider, predictivePinDropUseCaseProvider);
  }

  public static MainViewModel newInstance(BuildingRepository buildingRepository,
      TrajectoryRepository trajectoryRepository,
      DeliverySessionRepository deliverySessionRepository,
      ComputeThermalProjectionUseCase computeThermalProjectionUseCase,
      GenerateThermalRouteAdviceUseCase generateThermalRouteAdviceUseCase,
      GenerateAlertsUseCase generateAlertsUseCase,
      PredictivePinDropUseCase predictivePinDropUseCase) {
    return new MainViewModel(buildingRepository, trajectoryRepository, deliverySessionRepository, computeThermalProjectionUseCase, generateThermalRouteAdviceUseCase, generateAlertsUseCase, predictivePinDropUseCase);
  }
}
