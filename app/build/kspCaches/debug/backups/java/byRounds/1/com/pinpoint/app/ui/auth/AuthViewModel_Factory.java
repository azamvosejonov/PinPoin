package com.pinpoint.app.ui.auth;

import com.pinpoint.app.data.TokenManager;
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
public final class AuthViewModel_Factory implements Factory<AuthViewModel> {
  private final Provider<BackendRepository> backendRepositoryProvider;

  private final Provider<TokenManager> tokenManagerProvider;

  public AuthViewModel_Factory(Provider<BackendRepository> backendRepositoryProvider,
      Provider<TokenManager> tokenManagerProvider) {
    this.backendRepositoryProvider = backendRepositoryProvider;
    this.tokenManagerProvider = tokenManagerProvider;
  }

  @Override
  public AuthViewModel get() {
    return newInstance(backendRepositoryProvider.get(), tokenManagerProvider.get());
  }

  public static AuthViewModel_Factory create(Provider<BackendRepository> backendRepositoryProvider,
      Provider<TokenManager> tokenManagerProvider) {
    return new AuthViewModel_Factory(backendRepositoryProvider, tokenManagerProvider);
  }

  public static AuthViewModel newInstance(BackendRepository backendRepository,
      TokenManager tokenManager) {
    return new AuthViewModel(backendRepository, tokenManager);
  }
}
