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
public final class ComputeBuildingDifficultyUseCase_Factory implements Factory<ComputeBuildingDifficultyUseCase> {
  @Override
  public ComputeBuildingDifficultyUseCase get() {
    return newInstance();
  }

  public static ComputeBuildingDifficultyUseCase_Factory create() {
    return InstanceHolder.INSTANCE;
  }

  public static ComputeBuildingDifficultyUseCase newInstance() {
    return new ComputeBuildingDifficultyUseCase();
  }

  private static final class InstanceHolder {
    private static final ComputeBuildingDifficultyUseCase_Factory INSTANCE = new ComputeBuildingDifficultyUseCase_Factory();
  }
}
