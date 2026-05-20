package com.pinpoint.app.di;

import com.pinpoint.app.data.remote.geocoding.GeocodingRemoteDataSource;
import com.pinpoint.app.data.remote.geocoding.NominatimApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

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
public final class NetworkModule_ProvideGeocodingRemoteDataSourceFactory implements Factory<GeocodingRemoteDataSource> {
  private final Provider<NominatimApi> apiProvider;

  public NetworkModule_ProvideGeocodingRemoteDataSourceFactory(Provider<NominatimApi> apiProvider) {
    this.apiProvider = apiProvider;
  }

  @Override
  public GeocodingRemoteDataSource get() {
    return provideGeocodingRemoteDataSource(apiProvider.get());
  }

  public static NetworkModule_ProvideGeocodingRemoteDataSourceFactory create(
      Provider<NominatimApi> apiProvider) {
    return new NetworkModule_ProvideGeocodingRemoteDataSourceFactory(apiProvider);
  }

  public static GeocodingRemoteDataSource provideGeocodingRemoteDataSource(NominatimApi api) {
    return Preconditions.checkNotNullFromProvides(NetworkModule.INSTANCE.provideGeocodingRemoteDataSource(api));
  }
}
