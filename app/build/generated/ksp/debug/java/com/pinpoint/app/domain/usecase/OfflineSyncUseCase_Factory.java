package com.pinpoint.app.domain.usecase;

import com.pinpoint.app.domain.repository.BuildingRepository;
import com.pinpoint.app.domain.repository.TrajectoryRepository;
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
public final class OfflineSyncUseCase_Factory implements Factory<OfflineSyncUseCase> {
  private final Provider<BuildingRepository> buildingRepositoryProvider;

  private final Provider<TrajectoryRepository> trajectoryRepositoryProvider;

  public OfflineSyncUseCase_Factory(Provider<BuildingRepository> buildingRepositoryProvider,
      Provider<TrajectoryRepository> trajectoryRepositoryProvider) {
    this.buildingRepositoryProvider = buildingRepositoryProvider;
    this.trajectoryRepositoryProvider = trajectoryRepositoryProvider;
  }

  @Override
  public OfflineSyncUseCase get() {
    return newInstance(buildingRepositoryProvider.get(), trajectoryRepositoryProvider.get());
  }

  public static OfflineSyncUseCase_Factory create(
      Provider<BuildingRepository> buildingRepositoryProvider,
      Provider<TrajectoryRepository> trajectoryRepositoryProvider) {
    return new OfflineSyncUseCase_Factory(buildingRepositoryProvider, trajectoryRepositoryProvider);
  }

  public static OfflineSyncUseCase newInstance(BuildingRepository buildingRepository,
      TrajectoryRepository trajectoryRepository) {
    return new OfflineSyncUseCase(buildingRepository, trajectoryRepository);
  }
}
