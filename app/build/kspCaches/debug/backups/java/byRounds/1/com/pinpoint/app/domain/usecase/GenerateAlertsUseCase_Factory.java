package com.pinpoint.app.domain.usecase;

import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;

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
public final class GenerateAlertsUseCase_Factory implements Factory<GenerateAlertsUseCase> {
  @Override
  public GenerateAlertsUseCase get() {
    return newInstance();
  }

  public static GenerateAlertsUseCase_Factory create() {
    return InstanceHolder.INSTANCE;
  }

  public static GenerateAlertsUseCase newInstance() {
    return new GenerateAlertsUseCase();
  }

  private static final class InstanceHolder {
    private static final GenerateAlertsUseCase_Factory INSTANCE = new GenerateAlertsUseCase_Factory();
  }
}
