package com.pinpoint.app.ui.indoor;

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
public final class IndoorMapViewModel_Factory implements Factory<IndoorMapViewModel> {
  private final Provider<BackendRepository> backendRepositoryProvider;

  public IndoorMapViewModel_Factory(Provider<BackendRepository> backendRepositoryProvider) {
    this.backendRepositoryProvider = backendRepositoryProvider;
  }

  @Override
  public IndoorMapViewModel get() {
    return newInstance(backendRepositoryProvider.get());
  }

  public static IndoorMapViewModel_Factory create(
      Provider<BackendRepository> backendRepositoryProvider) {
    return new IndoorMapViewModel_Factory(backendRepositoryProvider);
  }

  public static IndoorMapViewModel newInstance(BackendRepository backendRepository) {
    return new IndoorMapViewModel(backendRepository);
  }
}
