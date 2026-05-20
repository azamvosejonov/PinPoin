package com.pinpoint.app.data.repository;

import com.pinpoint.app.data.local.dao.TrajectoryDao;
import com.pinpoint.app.data.remote.backend.BackendApi;
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
public final class TrajectoryRepositoryImpl_Factory implements Factory<TrajectoryRepositoryImpl> {
  private final Provider<TrajectoryDao> trajectoryDaoProvider;

  private final Provider<BackendApi> backendApiProvider;

  public TrajectoryRepositoryImpl_Factory(Provider<TrajectoryDao> trajectoryDaoProvider,
      Provider<BackendApi> backendApiProvider) {
    this.trajectoryDaoProvider = trajectoryDaoProvider;
    this.backendApiProvider = backendApiProvider;
  }

  @Override
  public TrajectoryRepositoryImpl get() {
    return newInstance(trajectoryDaoProvider.get(), backendApiProvider.get());
  }

  public static TrajectoryRepositoryImpl_Factory create(
      Provider<TrajectoryDao> trajectoryDaoProvider, Provider<BackendApi> backendApiProvider) {
    return new TrajectoryRepositoryImpl_Factory(trajectoryDaoProvider, backendApiProvider);
  }

  public static TrajectoryRepositoryImpl newInstance(TrajectoryDao trajectoryDao,
      BackendApi backendApi) {
    return new TrajectoryRepositoryImpl(trajectoryDao, backendApi);
  }
}
