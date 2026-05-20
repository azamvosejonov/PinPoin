package com.pinpoint.app.di;

import com.pinpoint.app.domain.usecase.GenerateAlertsUseCase;
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
public final class UseCaseModule_ProvideGenerateAlertsUseCaseFactory implements Factory<GenerateAlertsUseCase> {
  @Override
  public GenerateAlertsUseCase get() {
    return provideGenerateAlertsUseCase();
  }

  public static UseCaseModule_ProvideGenerateAlertsUseCaseFactory create() {
    return InstanceHolder.INSTANCE;
  }

  public static GenerateAlertsUseCase provideGenerateAlertsUseCase() {
    return Preconditions.checkNotNullFromProvides(UseCaseModule.INSTANCE.provideGenerateAlertsUseCase());
  }

  private static final class InstanceHolder {
    private static final UseCaseModule_ProvideGenerateAlertsUseCaseFactory INSTANCE = new UseCaseModule_ProvideGenerateAlertsUseCaseFactory();
  }
}
