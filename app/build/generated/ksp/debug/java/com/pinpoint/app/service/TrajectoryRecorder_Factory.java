package com.pinpoint.app.service;

import com.pinpoint.app.domain.repository.TrajectoryRepository;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
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
public final class TrajectoryRecorder_Factory implements Factory<TrajectoryRecorder> {
  private final Provider<TrajectoryRepository> trajectoryRepositoryProvider;

  public TrajectoryRecorder_Factory(Provider<TrajectoryRepository> trajectoryRepositoryProvider) {
    this.trajectoryRepositoryProvider = trajectoryRepositoryProvider;
  }

  @Override
  public TrajectoryRecorder get() {
    return newInstance(trajectoryRepositoryProvider.get());
  }

  public static TrajectoryRecorder_Factory create(
      Provider<TrajectoryRepository> trajectoryRepositoryProvider) {
    return new TrajectoryRecorder_Factory(trajectoryRepositoryProvider);
  }

  public static TrajectoryRecorder newInstance(TrajectoryRepository trajectoryRepository) {
    return new TrajectoryRecorder(trajectoryRepository);
  }
}
