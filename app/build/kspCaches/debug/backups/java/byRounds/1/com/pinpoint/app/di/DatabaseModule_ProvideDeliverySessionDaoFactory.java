package com.pinpoint.app.di;

import com.pinpoint.app.data.local.PinPoIntDatabase;
import com.pinpoint.app.data.local.dao.DeliverySessionDao;
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
public final class DatabaseModule_ProvideDeliverySessionDaoFactory implements Factory<DeliverySessionDao> {
  private final Provider<PinPoIntDatabase> databaseProvider;

  public DatabaseModule_ProvideDeliverySessionDaoFactory(
      Provider<PinPoIntDatabase> databaseProvider) {
    this.databaseProvider = databaseProvider;
  }

  @Override
  public DeliverySessionDao get() {
    return provideDeliverySessionDao(databaseProvider.get());
  }

  public static DatabaseModule_ProvideDeliverySessionDaoFactory create(
      Provider<PinPoIntDatabase> databaseProvider) {
    return new DatabaseModule_ProvideDeliverySessionDaoFactory(databaseProvider);
  }

  public static DeliverySessionDao provideDeliverySessionDao(PinPoIntDatabase database) {
    return Preconditions.checkNotNullFromProvides(DatabaseModule.INSTANCE.provideDeliverySessionDao(database));
  }
}
