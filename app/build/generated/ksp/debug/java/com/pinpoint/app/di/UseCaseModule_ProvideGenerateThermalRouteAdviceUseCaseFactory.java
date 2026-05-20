package com.pinpoint.app.di;

import com.pinpoint.app.domain.usecase.ComputeBuildingDifficultyUseCase;
import com.pinpoint.app.domain.usecase.GenerateThermalRouteAdviceUseCase;
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
public final class UseCaseModule_ProvideGenerateThermalRouteAdviceUseCaseFactory implements Factory<GenerateThermalRouteAdviceUseCase> {
  private final Provider<ComputeBuildingDifficultyUseCase> computeBuildingDifficultyUseCaseProvider;

  public UseCaseModule_ProvideGenerateThermalRouteAdviceUseCaseFactory(
      Provider<ComputeBuildingDifficultyUseCase> computeBuildingDifficultyUseCaseProvider) {
    this.computeBuildingDifficultyUseCaseProvider = computeBuildingDifficultyUseCaseProvider;
  }

  @Override
  public GenerateThermalRouteAdviceUseCase get() {
    return provideGenerateThermalRouteAdviceUseCase(computeBuildingDifficultyUseCaseProvider.get());
  }

  public static UseCaseModule_ProvideGenerateThermalRouteAdviceUseCaseFactory create(
      Provider<ComputeBuildingDifficultyUseCase> computeBuildingDifficultyUseCaseProvider) {
    return new UseCaseModule_ProvideGenerateThermalRouteAdviceUseCaseFactory(computeBuildingDifficultyUseCaseProvider);
  }

  public static GenerateThermalRouteAdviceUseCase provideGenerateThermalRouteAdviceUseCase(
      ComputeBuildingDifficultyUseCase computeBuildingDifficultyUseCase) {
    return Preconditions.checkNotNullFromProvides(UseCaseModule.INSTANCE.provideGenerateThermalRouteAdviceUseCase(computeBuildingDifficultyUseCase));
  }
}
