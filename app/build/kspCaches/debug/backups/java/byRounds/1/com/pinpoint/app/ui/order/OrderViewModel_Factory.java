package com.pinpoint.app.ui.order;

import com.pinpoint.app.domain.repository.OrderRepository;
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
public final class OrderViewModel_Factory implements Factory<OrderViewModel> {
  private final Provider<OrderRepository> orderRepositoryProvider;

  public OrderViewModel_Factory(Provider<OrderRepository> orderRepositoryProvider) {
    this.orderRepositoryProvider = orderRepositoryProvider;
  }

  @Override
  public OrderViewModel get() {
    return newInstance(orderRepositoryProvider.get());
  }

  public static OrderViewModel_Factory create(Provider<OrderRepository> orderRepositoryProvider) {
    return new OrderViewModel_Factory(orderRepositoryProvider);
  }

  public static OrderViewModel newInstance(OrderRepository orderRepository) {
    return new OrderViewModel(orderRepository);
  }
}
