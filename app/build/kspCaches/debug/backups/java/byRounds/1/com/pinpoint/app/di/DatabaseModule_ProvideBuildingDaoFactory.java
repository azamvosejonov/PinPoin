package com.pinpoint.app.di;

import com.pinpoint.app.data.local.PinPoIntDatabase;
import com.pinpoint.app.data.local.dao.BuildingDao;
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
public final class DatabaseModule_ProvideBuildingDaoFactory implements Factory<BuildingDao> {
  private final Provider<PinPoIntDatabase> databaseProvider;

  public DatabaseModule_ProvideBuildingDaoFactory(Provider<PinPoIntDatabase> databaseProvider) {
    this.databaseProvider = databaseProvider;
  }

  @Override
  public BuildingDao get() {
    return provideBuildingDao(databaseProvider.get());
  }

  public static DatabaseModule_ProvideBuildingDaoFactory create(
      Provider<PinPoIntDatabase> databaseProvider) {
    return new DatabaseModule_ProvideBuildingDaoFactory(databaseProvider);
  }

  public static BuildingDao provideBuildingDao(PinPoIntDatabase database) {
    return Preconditions.checkNotNullFromProvides(DatabaseModule.INSTANCE.provideBuildingDao(database));
  }
}
