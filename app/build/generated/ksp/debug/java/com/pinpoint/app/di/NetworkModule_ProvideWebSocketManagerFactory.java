package com.pinpoint.app.di;

import com.google.gson.Gson;
import com.pinpoint.app.data.websocket.WebSocketManager;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;
import okhttp3.OkHttpClient;

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
public final class NetworkModule_ProvideWebSocketManagerFactory implements Factory<WebSocketManager> {
  private final Provider<OkHttpClient> okHttpClientProvider;

  private final Provider<Gson> gsonProvider;

  public NetworkModule_ProvideWebSocketManagerFactory(Provider<OkHttpClient> okHttpClientProvider,
      Provider<Gson> gsonProvider) {
    this.okHttpClientProvider = okHttpClientProvider;
    this.gsonProvider = gsonProvider;
  }

  @Override
  public WebSocketManager get() {
    return provideWebSocketManager(okHttpClientProvider.get(), gsonProvider.get());
  }

  public static NetworkModule_ProvideWebSocketManagerFactory create(
      Provider<OkHttpClient> okHttpClientProvider, Provider<Gson> gsonProvider) {
    return new NetworkModule_ProvideWebSocketManagerFactory(okHttpClientProvider, gsonProvider);
  }

  public static WebSocketManager provideWebSocketManager(OkHttpClient okHttpClient, Gson gson) {
    return Preconditions.checkNotNullFromProvides(NetworkModule.INSTANCE.provideWebSocketManager(okHttpClient, gson));
  }
}
