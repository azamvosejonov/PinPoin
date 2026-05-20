package com.pinpoint.app.di;

import com.pinpoint.app.data.remote.geocoding.NominatimApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;
import retrofit2.Retrofit;

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
public final class NetworkModule_ProvideNominatimApiFactory implements Factory<NominatimApi> {
  private final Provider<Retrofit> retrofitProvider;

  public NetworkModule_ProvideNominatimApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public NominatimApi get() {
    return provideNominatimApi(retrofitProvider.get());
  }

  public static NetworkModule_ProvideNominatimApiFactory create(
      Provider<Retrofit> retrofitProvider) {
    return new NetworkModule_ProvideNominatimApiFactory(retrofitProvider);
  }

  public static NominatimApi provideNominatimApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(NetworkModule.INSTANCE.provideNominatimApi(retrofit));
  }
}
