package com.pinpoint.app.di;

import com.google.gson.Gson;
import com.pinpoint.app.data.remote.backend.BackendApi;
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
public final class NetworkModule_ProvideBackendApiFactory implements Factory<BackendApi> {
  private final Provider<OkHttpClient> clientProvider;

  private final Provider<Gson> gsonProvider;

  public NetworkModule_ProvideBackendApiFactory(Provider<OkHttpClient> clientProvider,
      Provider<Gson> gsonProvider) {
    this.clientProvider = clientProvider;
    this.gsonProvider = gsonProvider;
  }

  @Override
  public BackendApi get() {
    return provideBackendApi(clientProvider.get(), gsonProvider.get());
  }

  public static NetworkModule_ProvideBackendApiFactory create(Provider<OkHttpClient> clientProvider,
      Provider<Gson> gsonProvider) {
    return new NetworkModule_ProvideBackendApiFactory(clientProvider, gsonProvider);
  }

  public static BackendApi provideBackendApi(OkHttpClient client, Gson gson) {
    return Preconditions.checkNotNullFromProvides(NetworkModule.INSTANCE.provideBackendApi(client, gson));
  }
}
