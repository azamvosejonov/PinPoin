package com.pinpoint.app.ui.location;

import com.google.android.gms.location.FusedLocationProviderClient;
import com.pinpoint.app.data.websocket.WebSocketManager;
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
public final class CourierLocationViewModel_Factory implements Factory<CourierLocationViewModel> {
  private final Provider<BackendRepository> backendRepositoryProvider;

  private final Provider<WebSocketManager> webSocketManagerProvider;

  private final Provider<FusedLocationProviderClient> fusedLocationClientProvider;

  public CourierLocationViewModel_Factory(Provider<BackendRepository> backendRepositoryProvider,
      Provider<WebSocketManager> webSocketManagerProvider,
      Provider<FusedLocationProviderClient> fusedLocationClientProvider) {
    this.backendRepositoryProvider = backendRepositoryProvider;
    this.webSocketManagerProvider = webSocketManagerProvider;
    this.fusedLocationClientProvider = fusedLocationClientProvider;
  }

  @Override
  public CourierLocationViewModel get() {
    return newInstance(backendRepositoryProvider.get(), webSocketManagerProvider.get(), fusedLocationClientProvider.get());
  }

  public static CourierLocationViewModel_Factory create(
      Provider<BackendRepository> backendRepositoryProvider,
      Provider<WebSocketManager> webSocketManagerProvider,
      Provider<FusedLocationProviderClient> fusedLocationClientProvider) {
    return new CourierLocationViewModel_Factory(backendRepositoryProvider, webSocketManagerProvider, fusedLocationClientProvider);
  }

  public static CourierLocationViewModel newInstance(BackendRepository backendRepository,
      WebSocketManager webSocketManager, FusedLocationProviderClient fusedLocationClient) {
    return new CourierLocationViewModel(backendRepository, webSocketManager, fusedLocationClient);
  }
}
