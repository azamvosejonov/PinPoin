package com.pinpoint.app.di;

import com.pinpoint.app.data.remote.backend.BackendRemoteDataSource;
import com.pinpoint.app.domain.usecase.PredictivePinDropUseCase;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
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
public final class UseCaseModule_ProvidePredictivePinDropUseCaseFactory implements Factory<PredictivePinDropUseCase> {
  private final Provider<BackendRemoteDataSource> backendRemoteDataSourceProvider;

  public UseCaseModule_ProvidePredictivePinDropUseCaseFactory(
      Provider<BackendRemoteDataSource> backendRemoteDataSourceProvider) {
    this.backendRemoteDataSourceProvider = backendRemoteDataSourceProvider;
  }

  @Override
  public PredictivePinDropUseCase get() {
    return providePredictivePinDropUseCase(backendRemoteDataSourceProvider.get());
  }

  public static UseCaseModule_ProvidePredictivePinDropUseCaseFactory create(
      Provider<BackendRemoteDataSource> backendRemoteDataSourceProvider) {
    return new UseCaseModule_ProvidePredictivePinDropUseCaseFactory(backendRemoteDataSourceProvider);
  }

  public static PredictivePinDropUseCase providePredictivePinDropUseCase(
      BackendRemoteDataSource backendRemoteDataSource) {
    return Preconditions.checkNotNullFromProvides(UseCaseModule.INSTANCE.providePredictivePinDropUseCase(backendRemoteDataSource));
  }
}
