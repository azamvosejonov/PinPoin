package com.pinpoint.app.domain.usecase;

import com.pinpoint.app.data.remote.backend.BackendRemoteDataSource;
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
public final class PredictivePinDropUseCase_Factory implements Factory<PredictivePinDropUseCase> {
  private final Provider<BackendRemoteDataSource> backendRemoteDataSourceProvider;

  public PredictivePinDropUseCase_Factory(
      Provider<BackendRemoteDataSource> backendRemoteDataSourceProvider) {
    this.backendRemoteDataSourceProvider = backendRemoteDataSourceProvider;
  }

  @Override
  public PredictivePinDropUseCase get() {
    return newInstance(backendRemoteDataSourceProvider.get());
  }

  public static PredictivePinDropUseCase_Factory create(
      Provider<BackendRemoteDataSource> backendRemoteDataSourceProvider) {
    return new PredictivePinDropUseCase_Factory(backendRemoteDataSourceProvider);
  }

  public static PredictivePinDropUseCase newInstance(
      BackendRemoteDataSource backendRemoteDataSource) {
    return new PredictivePinDropUseCase(backendRemoteDataSource);
  }
}
