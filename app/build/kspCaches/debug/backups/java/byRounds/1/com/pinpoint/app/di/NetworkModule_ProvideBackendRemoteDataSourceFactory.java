package com.pinpoint.app.di;

import com.pinpoint.app.data.remote.backend.BackendApi;
import com.pinpoint.app.data.remote.backend.BackendRemoteDataSource;
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
public final class NetworkModule_ProvideBackendRemoteDataSourceFactory implements Factory<BackendRemoteDataSource> {
  private final Provider<BackendApi> apiProvider;

  public NetworkModule_ProvideBackendRemoteDataSourceFactory(Provider<BackendApi> apiProvider) {
    this.apiProvider = apiProvider;
  }

  @Override
  public BackendRemoteDataSource get() {
    return provideBackendRemoteDataSource(apiProvider.get());
  }

  public static NetworkModule_ProvideBackendRemoteDataSourceFactory create(
      Provider<BackendApi> apiProvider) {
    return new NetworkModule_ProvideBackendRemoteDataSourceFactory(apiProvider);
  }

  public static BackendRemoteDataSource provideBackendRemoteDataSource(BackendApi api) {
    return Preconditions.checkNotNullFromProvides(NetworkModule.INSTANCE.provideBackendRemoteDataSource(api));
  }
}
