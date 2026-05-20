package com.pinpoint.app.data.repository;

import com.pinpoint.app.data.local.dao.DeliverySessionDao;
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
public final class DeliverySessionRepositoryImpl_Factory implements Factory<DeliverySessionRepositoryImpl> {
  private final Provider<DeliverySessionDao> daoProvider;

  public DeliverySessionRepositoryImpl_Factory(Provider<DeliverySessionDao> daoProvider) {
    this.daoProvider = daoProvider;
  }

  @Override
  public DeliverySessionRepositoryImpl get() {
    return newInstance(daoProvider.get());
  }

  public static DeliverySessionRepositoryImpl_Factory create(
      Provider<DeliverySessionDao> daoProvider) {
    return new DeliverySessionRepositoryImpl_Factory(daoProvider);
  }

  public static DeliverySessionRepositoryImpl newInstance(DeliverySessionDao dao) {
    return new DeliverySessionRepositoryImpl(dao);
  }
}
