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
public final class AlertDispatcher_Factory implements Factory<AlertDispatcher> {
  private final Provider<Context> contextProvider;

  public AlertDispatcher_Factory(Provider<Context> contextProvider) {
    this.contextProvider = contextProvider;
  }

  @Override
  public AlertDispatcher get() {
    return newInstance(contextProvider.get());
  }

  public static AlertDispatcher_Factory create(Provider<Context> contextProvider) {
    return new AlertDispatcher_Factory(contextProvider);
  }

  public static AlertDispatcher newInstance(Context context) {
    return new AlertDispatcher(context);
  }
}
