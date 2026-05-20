package com.pinpoint.app.data.remote.backend;

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
public final class BackendRemoteDataSource_Factory implements Factory<BackendRemoteDataSource> {
  private final Provider<BackendApi> apiProvider;

  public BackendRemoteDataSource_Factory(Provider<BackendApi> apiProvider) {
    this.apiProvider = apiProvider;
  }

  @Override
  public BackendRemoteDataSource get() {
    return newInstance(apiProvider.get());
  }

  public static BackendRemoteDataSource_Factory create(Provider<BackendApi> apiProvider) {
    return new BackendRemoteDataSource_Factory(apiProvider);
  }

  public static BackendRemoteDataSource newInstance(BackendApi api) {
    return new BackendRemoteDataSource(api);
  }
}
