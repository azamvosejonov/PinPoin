package com.pinpoint.app.data.remote.geocoding;

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
public final class GeocodingRemoteDataSource_Factory implements Factory<GeocodingRemoteDataSource> {
  private final Provider<NominatimApi> apiProvider;

  public GeocodingRemoteDataSource_Factory(Provider<NominatimApi> apiProvider) {
    this.apiProvider = apiProvider;
  }

  @Override
  public GeocodingRemoteDataSource get() {
    return newInstance(apiProvider.get());
  }

  public static GeocodingRemoteDataSource_Factory create(Provider<NominatimApi> apiProvider) {
    return new GeocodingRemoteDataSource_Factory(apiProvider);
  }

  public static GeocodingRemoteDataSource newInstance(NominatimApi api) {
    return new GeocodingRemoteDataSource(api);
  }
}
