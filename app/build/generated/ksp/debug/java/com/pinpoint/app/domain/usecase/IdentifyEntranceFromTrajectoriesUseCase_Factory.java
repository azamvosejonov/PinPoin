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
public final class IdentifyEntranceFromTrajectoriesUseCase_Factory implements Factory<IdentifyEntranceFromTrajectoriesUseCase> {
  @Override
  public IdentifyEntranceFromTrajectoriesUseCase get() {
    return newInstance();
  }

  public static IdentifyEntranceFromTrajectoriesUseCase_Factory create() {
    return InstanceHolder.INSTANCE;
  }

  public static IdentifyEntranceFromTrajectoriesUseCase newInstance() {
    return new IdentifyEntranceFromTrajectoriesUseCase();
  }

  private static final class InstanceHolder {
    private static final IdentifyEntranceFromTrajectoriesUseCase_Factory INSTANCE = new IdentifyEntranceFromTrajectoriesUseCase_Factory();
  }
}
