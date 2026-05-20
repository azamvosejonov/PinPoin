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
public final class AnalyzeTrajectoryUseCase_Factory implements Factory<AnalyzeTrajectoryUseCase> {
  @Override
  public AnalyzeTrajectoryUseCase get() {
    return newInstance();
  }

  public static AnalyzeTrajectoryUseCase_Factory create() {
    return InstanceHolder.INSTANCE;
  }

  public static AnalyzeTrajectoryUseCase newInstance() {
    return new AnalyzeTrajectoryUseCase();
  }

  private static final class InstanceHolder {
    private static final AnalyzeTrajectoryUseCase_Factory INSTANCE = new AnalyzeTrajectoryUseCase_Factory();
  }
}
