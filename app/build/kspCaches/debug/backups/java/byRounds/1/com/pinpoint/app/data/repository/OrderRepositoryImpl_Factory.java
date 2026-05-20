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
public final class OrderRepositoryImpl_Factory implements Factory<OrderRepositoryImpl> {
  private final Provider<BackendApi> backendApiProvider;

  public OrderRepositoryImpl_Factory(Provider<BackendApi> backendApiProvider) {
    this.backendApiProvider = backendApiProvider;
  }

  @Override
  public OrderRepositoryImpl get() {
    return newInstance(backendApiProvider.get());
  }

  public static OrderRepositoryImpl_Factory create(Provider<BackendApi> backendApiProvider) {
    return new OrderRepositoryImpl_Factory(backendApiProvider);
  }

  public static OrderRepositoryImpl newInstance(BackendApi backendApi) {
    return new OrderRepositoryImpl(backendApi);
  }
}
