package com.pinpoint.app.di;

import com.pinpoint.app.domain.usecase.ComputeBuildingDifficultyUseCase;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;

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
public final class UseCaseModule_ProvideComputeBuildingDifficultyUseCaseFactory implements Factory<ComputeBuildingDifficultyUseCase> {
  @Override
  public ComputeBuildingDifficultyUseCase get() {
    return provideComputeBuildingDifficultyUseCase();
  }

  public static UseCaseModule_ProvideComputeBuildingDifficultyUseCaseFactory create() {
    return InstanceHolder.INSTANCE;
  }

  public static ComputeBuildingDifficultyUseCase provideComputeBuildingDifficultyUseCase() {
    return Preconditions.checkNotNullFromProvides(UseCaseModule.INSTANCE.provideComputeBuildingDifficultyUseCase());
  }

  private static final class InstanceHolder {
    private static final UseCaseModule_ProvideComputeBuildingDifficultyUseCaseFactory INSTANCE = new UseCaseModule_ProvideComputeBuildingDifficultyUseCaseFactory();
  }
}
