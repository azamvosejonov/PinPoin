package com.pinpoint.app.ui.restaurant;

import com.pinpoint.app.domain.repository.BackendRepository;
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
public final class RestaurantViewModel_Factory implements Factory<RestaurantViewModel> {
  private final Provider<BackendRepository> backendRepositoryProvider;

  public RestaurantViewModel_Factory(Provider<BackendRepository> backendRepositoryProvider) {
    this.backendRepositoryProvider = backendRepositoryProvider;
  }

  @Override
  public RestaurantViewModel get() {
    return newInstance(backendRepositoryProvider.get());
  }

  public static RestaurantViewModel_Factory create(
      Provider<BackendRepository> backendRepositoryProvider) {
    return new RestaurantViewModel_Factory(backendRepositoryProvider);
  }

  public static RestaurantViewModel newInstance(BackendRepository backendRepository) {
    return new RestaurantViewModel(backendRepository);
  }
}
