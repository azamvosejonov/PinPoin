package com.pinpoint.app.data.repository;

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
public final class BackendRepositoryImpl_Factory implements Factory<BackendRepositoryImpl> {
  private final Provider<BackendApi> backendApiProvider;

  public BackendRepositoryImpl_Factory(Provider<BackendApi> backendApiProvider) {
    this.backendApiProvider = backendApiProvider;
  }

  @Override
  public BackendRepositoryImpl get() {
    return newInstance(backendApiProvider.get());
  }

  public static BackendRepositoryImpl_Factory create(Provider<BackendApi> backendApiProvider) {
    return new BackendRepositoryImpl_Factory(backendApiProvider);
  }

  public static BackendRepositoryImpl newInstance(BackendApi backendApi) {
    return new BackendRepositoryImpl(backendApi);
  }
}
