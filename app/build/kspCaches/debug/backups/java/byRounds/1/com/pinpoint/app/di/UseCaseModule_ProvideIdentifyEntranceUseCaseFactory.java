package com.pinpoint.app.di;

import com.pinpoint.app.domain.usecase.IdentifyEntranceFromTrajectoriesUseCase;
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
public final class UseCaseModule_ProvideIdentifyEntranceUseCaseFactory implements Factory<IdentifyEntranceFromTrajectoriesUseCase> {
  @Override
  public IdentifyEntranceFromTrajectoriesUseCase get() {
    return provideIdentifyEntranceUseCase();
  }

  public static UseCaseModule_ProvideIdentifyEntranceUseCaseFactory create() {
    return InstanceHolder.INSTANCE;
  }

  public static IdentifyEntranceFromTrajectoriesUseCase provideIdentifyEntranceUseCase() {
    return Preconditions.checkNotNullFromProvides(UseCaseModule.INSTANCE.provideIdentifyEntranceUseCase());
  }

  private static final class InstanceHolder {
    private static final UseCaseModule_ProvideIdentifyEntranceUseCaseFactory INSTANCE = new UseCaseModule_ProvideIdentifyEntranceUseCaseFactory();
  }
}
