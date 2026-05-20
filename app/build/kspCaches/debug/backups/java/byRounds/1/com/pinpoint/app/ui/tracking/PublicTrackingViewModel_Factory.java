package com.pinpoint.app.ui.tracking;

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
public final class PublicTrackingViewModel_Factory implements Factory<PublicTrackingViewModel> {
  private final Provider<BackendRepository> backendRepositoryProvider;

  public PublicTrackingViewModel_Factory(Provider<BackendRepository> backendRepositoryProvider) {
    this.backendRepositoryProvider = backendRepositoryProvider;
  }

  @Override
  public PublicTrackingViewModel get() {
    return newInstance(backendRepositoryProvider.get());
  }

  public static PublicTrackingViewModel_Factory create(
      Provider<BackendRepository> backendRepositoryProvider) {
    return new PublicTrackingViewModel_Factory(backendRepositoryProvider);
  }

  public static PublicTrackingViewModel newInstance(BackendRepository backendRepository) {
    return new PublicTrackingViewModel(backendRepository);
  }
}
