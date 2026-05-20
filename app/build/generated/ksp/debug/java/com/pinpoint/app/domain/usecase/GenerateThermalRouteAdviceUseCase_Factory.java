package com.pinpoint.app.domain.usecase;

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
public final class GenerateThermalRouteAdviceUseCase_Factory implements Factory<GenerateThermalRouteAdviceUseCase> {
  private final Provider<ComputeBuildingDifficultyUseCase> computeBuildingDifficultyUseCaseProvider;

  public GenerateThermalRouteAdviceUseCase_Factory(
      Provider<ComputeBuildingDifficultyUseCase> computeBuildingDifficultyUseCaseProvider) {
    this.computeBuildingDifficultyUseCaseProvider = computeBuildingDifficultyUseCaseProvider;
  }

  @Override
  public GenerateThermalRouteAdviceUseCase get() {
    return newInstance(computeBuildingDifficultyUseCaseProvider.get());
  }

  public static GenerateThermalRouteAdviceUseCase_Factory create(
      Provider<ComputeBuildingDifficultyUseCase> computeBuildingDifficultyUseCaseProvider) {
    return new GenerateThermalRouteAdviceUseCase_Factory(computeBuildingDifficultyUseCaseProvider);
  }

  public static GenerateThermalRouteAdviceUseCase newInstance(
      ComputeBuildingDifficultyUseCase computeBuildingDifficultyUseCase) {
    return new GenerateThermalRouteAdviceUseCase(computeBuildingDifficultyUseCase);
  }
}
