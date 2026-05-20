package com.pinpoint.app.di;

import com.pinpoint.app.data.local.PinPoIntDatabase;
import com.pinpoint.app.data.local.dao.TrajectoryDao;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
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
public final class DatabaseModule_ProvideTrajectoryDaoFactory implements Factory<TrajectoryDao> {
  private final Provider<PinPoIntDatabase> databaseProvider;

  public DatabaseModule_ProvideTrajectoryDaoFactory(Provider<PinPoIntDatabase> databaseProvider) {
    this.databaseProvider = databaseProvider;
  }

  @Override
  public TrajectoryDao get() {
    return provideTrajectoryDao(databaseProvider.get());
  }

  public static DatabaseModule_ProvideTrajectoryDaoFactory create(
      Provider<PinPoIntDatabase> databaseProvider) {
    return new DatabaseModule_ProvideTrajectoryDaoFactory(databaseProvider);
  }

  public static TrajectoryDao provideTrajectoryDao(PinPoIntDatabase database) {
    return Preconditions.checkNotNullFromProvides(DatabaseModule.INSTANCE.provideTrajectoryDao(database));
  }
}
