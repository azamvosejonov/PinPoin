package com.pinpoint.app.data.repository;

import com.pinpoint.app.data.local.dao.BuildingDao;
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
public final class BuildingRepositoryImpl_Factory implements Factory<BuildingRepositoryImpl> {
  private final Provider<BuildingDao> buildingDaoProvider;

  private final Provider<BackendApi> backendApiProvider;

  public BuildingRepositoryImpl_Factory(Provider<BuildingDao> buildingDaoProvider,
      Provider<BackendApi> backendApiProvider) {
    this.buildingDaoProvider = buildingDaoProvider;
    this.backendApiProvider = backendApiProvider;
  }

  @Override
  public BuildingRepositoryImpl get() {
    return newInstance(buildingDaoProvider.get(), backendApiProvider.get());
  }

  public static BuildingRepositoryImpl_Factory create(Provider<BuildingDao> buildingDaoProvider,
      Provider<BackendApi> backendApiProvider) {
    return new BuildingRepositoryImpl_Factory(buildingDaoProvider, backendApiProvider);
  }

  public static BuildingRepositoryImpl newInstance(BuildingDao buildingDao, BackendApi backendApi) {
    return new BuildingRepositoryImpl(buildingDao, backendApi);
  }
}
