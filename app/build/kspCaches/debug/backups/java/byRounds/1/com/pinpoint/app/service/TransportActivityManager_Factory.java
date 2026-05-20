package com.pinpoint.app.service;

import android.content.Context;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
@QualifierMetadata("dagger.hilt.android.qualifiers.ApplicationContext")
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
public final class TransportActivityManager_Factory implements Factory<TransportActivityManager> {
  private final Provider<Context> contextProvider;

  public TransportActivityManager_Factory(Provider<Context> contextProvider) {
    this.contextProvider = contextProvider;
  }

  @Override
  public TransportActivityManager get() {
    return newInstance(contextProvider.get());
  }

  public static TransportActivityManager_Factory create(Provider<Context> contextProvider) {
    return new TransportActivityManager_Factory(contextProvider);
  }

  public static TransportActivityManager newInstance(Context context) {
    return new TransportActivityManager(context);
  }
}
