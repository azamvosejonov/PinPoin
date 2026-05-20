package com.pinpoint.app.di;

import com.pinpoint.app.domain.usecase.ComputeThermalProjectionUseCase;
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
public final class UseCaseModule_ProvideComputeThermalProjectionUseCaseFactory implements Factory<ComputeThermalProjectionUseCase> {
  @Override
  public ComputeThermalProjectionUseCase get() {
    return provideComputeThermalProjectionUseCase();
  }

  public static UseCaseModule_ProvideComputeThermalProjectionUseCaseFactory create() {
    return InstanceHolder.INSTANCE;
  }

  public static ComputeThermalProjectionUseCase provideComputeThermalProjectionUseCase() {
    return Preconditions.checkNotNullFromProvides(UseCaseModule.INSTANCE.provideComputeThermalProjectionUseCase());
  }

  private static final class InstanceHolder {
    private static final UseCaseModule_ProvideComputeThermalProjectionUseCaseFactory INSTANCE = new UseCaseModule_ProvideComputeThermalProjectionUseCaseFactory();
  }
}
