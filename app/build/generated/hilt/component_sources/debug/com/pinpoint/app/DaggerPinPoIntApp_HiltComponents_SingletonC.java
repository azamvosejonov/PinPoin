package com.pinpoint.app;

import android.app.Activity;
import android.app.Service;
import android.view.View;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.SavedStateHandle;
import androidx.lifecycle.ViewModel;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.errorprone.annotations.CanIgnoreReturnValue;
import com.google.gson.Gson;
import com.pinpoint.app.data.TokenManager;
import com.pinpoint.app.data.local.PinPoIntDatabase;
import com.pinpoint.app.data.local.dao.BuildingDao;
import com.pinpoint.app.data.local.dao.DeliverySessionDao;
import com.pinpoint.app.data.local.dao.TrajectoryDao;
import com.pinpoint.app.data.remote.backend.BackendApi;
import com.pinpoint.app.data.remote.backend.BackendRemoteDataSource;
import com.pinpoint.app.data.repository.BackendRepositoryImpl;
import com.pinpoint.app.data.repository.BuildingRepositoryImpl;
import com.pinpoint.app.data.repository.DeliverySessionRepositoryImpl;
import com.pinpoint.app.data.repository.OrderRepositoryImpl;
import com.pinpoint.app.data.repository.TrajectoryRepositoryImpl;
import com.pinpoint.app.data.websocket.WebSocketManager;
import com.pinpoint.app.di.DataModule;
import com.pinpoint.app.di.DataModule_ProvideTokenManagerFactory;
import com.pinpoint.app.di.DatabaseModule;
import com.pinpoint.app.di.DatabaseModule_ProvideBuildingDaoFactory;
import com.pinpoint.app.di.DatabaseModule_ProvideDatabaseFactory;
import com.pinpoint.app.di.DatabaseModule_ProvideDeliverySessionDaoFactory;
import com.pinpoint.app.di.DatabaseModule_ProvideTrajectoryDaoFactory;
import com.pinpoint.app.di.NetworkModule;
import com.pinpoint.app.di.NetworkModule_ProvideBackendApiFactory;
import com.pinpoint.app.di.NetworkModule_ProvideBackendRemoteDataSourceFactory;
import com.pinpoint.app.di.NetworkModule_ProvideFusedLocationProviderClientFactory;
import com.pinpoint.app.di.NetworkModule_ProvideGsonFactory;
import com.pinpoint.app.di.NetworkModule_ProvideOkHttpClientFactory;
import com.pinpoint.app.di.NetworkModule_ProvideWebSocketManagerFactory;
import com.pinpoint.app.di.UseCaseModule;
import com.pinpoint.app.di.UseCaseModule_ProvideComputeBuildingDifficultyUseCaseFactory;
import com.pinpoint.app.di.UseCaseModule_ProvideComputeThermalProjectionUseCaseFactory;
import com.pinpoint.app.di.UseCaseModule_ProvideGenerateAlertsUseCaseFactory;
import com.pinpoint.app.di.UseCaseModule_ProvideGenerateThermalRouteAdviceUseCaseFactory;
import com.pinpoint.app.di.UseCaseModule_ProvidePredictivePinDropUseCaseFactory;
import com.pinpoint.app.domain.repository.BackendRepository;
import com.pinpoint.app.domain.repository.BuildingRepository;
import com.pinpoint.app.domain.repository.DeliverySessionRepository;
import com.pinpoint.app.domain.repository.OrderRepository;
import com.pinpoint.app.domain.repository.TrajectoryRepository;
import com.pinpoint.app.domain.usecase.ComputeBuildingDifficultyUseCase;
import com.pinpoint.app.domain.usecase.ComputeThermalProjectionUseCase;
import com.pinpoint.app.domain.usecase.GenerateAlertsUseCase;
import com.pinpoint.app.domain.usecase.GenerateThermalRouteAdviceUseCase;
import com.pinpoint.app.domain.usecase.PredictivePinDropUseCase;
import com.pinpoint.app.service.ActivityRecognitionService;
import com.pinpoint.app.service.LocationTrackingService;
import com.pinpoint.app.service.LocationTrackingService_MembersInjector;
import com.pinpoint.app.service.TrajectoryRecorder;
import com.pinpoint.app.service.TransportActivityManager;
import com.pinpoint.app.ui.MainActivity;
import com.pinpoint.app.ui.MainViewModel;
import com.pinpoint.app.ui.MainViewModel_HiltModules_KeyModule_ProvideFactory;
import com.pinpoint.app.ui.auth.AuthViewModel;
import com.pinpoint.app.ui.auth.AuthViewModel_HiltModules_KeyModule_ProvideFactory;
import com.pinpoint.app.ui.indoor.IndoorMapViewModel;
import com.pinpoint.app.ui.indoor.IndoorMapViewModel_HiltModules_KeyModule_ProvideFactory;
import com.pinpoint.app.ui.location.CourierLocationViewModel;
import com.pinpoint.app.ui.location.CourierLocationViewModel_HiltModules_KeyModule_ProvideFactory;
import com.pinpoint.app.ui.order.OrderViewModel;
import com.pinpoint.app.ui.order.OrderViewModel_HiltModules_KeyModule_ProvideFactory;
import com.pinpoint.app.ui.restaurant.RestaurantViewModel;
import com.pinpoint.app.ui.restaurant.RestaurantViewModel_HiltModules_KeyModule_ProvideFactory;
import com.pinpoint.app.ui.tracking.PublicTrackingViewModel;
import com.pinpoint.app.ui.tracking.PublicTrackingViewModel_HiltModules_KeyModule_ProvideFactory;
import dagger.hilt.android.ActivityRetainedLifecycle;
import dagger.hilt.android.ViewModelLifecycle;
import dagger.hilt.android.flags.HiltWrapper_FragmentGetContextFix_FragmentGetContextFixModule;
import dagger.hilt.android.internal.builders.ActivityComponentBuilder;
import dagger.hilt.android.internal.builders.ActivityRetainedComponentBuilder;
import dagger.hilt.android.internal.builders.FragmentComponentBuilder;
import dagger.hilt.android.internal.builders.ServiceComponentBuilder;
import dagger.hilt.android.internal.builders.ViewComponentBuilder;
import dagger.hilt.android.internal.builders.ViewModelComponentBuilder;
import dagger.hilt.android.internal.builders.ViewWithFragmentComponentBuilder;
import dagger.hilt.android.internal.lifecycle.DefaultViewModelFactories;
import dagger.hilt.android.internal.lifecycle.DefaultViewModelFactories_InternalFactoryFactory_Factory;
import dagger.hilt.android.internal.managers.ActivityRetainedComponentManager_LifecycleModule_ProvideActivityRetainedLifecycleFactory;
import dagger.hilt.android.internal.modules.ApplicationContextModule;
import dagger.hilt.android.internal.modules.ApplicationContextModule_ProvideContextFactory;
import dagger.internal.DaggerGenerated;
import dagger.internal.DoubleCheck;
import dagger.internal.MapBuilder;
import dagger.internal.Preconditions;
import dagger.internal.SetBuilder;
import java.util.Collections;
import java.util.Map;
import java.util.Set;
import javax.annotation.processing.Generated;
import javax.inject.Provider;
import okhttp3.OkHttpClient;

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
public final class DaggerPinPoIntApp_HiltComponents_SingletonC {
  private DaggerPinPoIntApp_HiltComponents_SingletonC() {
  }

  public static Builder builder() {
    return new Builder();
  }

  public static final class Builder {
    private ApplicationContextModule applicationContextModule;

    private Builder() {
    }

    public Builder applicationContextModule(ApplicationContextModule applicationContextModule) {
      this.applicationContextModule = Preconditions.checkNotNull(applicationContextModule);
      return this;
    }

    /**
     * @deprecated This module is declared, but an instance is not used in the component. This method is a no-op. For more, see https://dagger.dev/unused-modules.
     */
    @Deprecated
    public Builder dataModule(DataModule dataModule) {
      Preconditions.checkNotNull(dataModule);
      return this;
    }

    /**
     * @deprecated This module is declared, but an instance is not used in the component. This method is a no-op. For more, see https://dagger.dev/unused-modules.
     */
    @Deprecated
    public Builder databaseModule(DatabaseModule databaseModule) {
      Preconditions.checkNotNull(databaseModule);
      return this;
    }

    /**
     * @deprecated This module is declared, but an instance is not used in the component. This method is a no-op. For more, see https://dagger.dev/unused-modules.
     */
    @Deprecated
    public Builder hiltWrapper_FragmentGetContextFix_FragmentGetContextFixModule(
        HiltWrapper_FragmentGetContextFix_FragmentGetContextFixModule hiltWrapper_FragmentGetContextFix_FragmentGetContextFixModule) {
      Preconditions.checkNotNull(hiltWrapper_FragmentGetContextFix_FragmentGetContextFixModule);
      return this;
    }

    /**
     * @deprecated This module is declared, but an instance is not used in the component. This method is a no-op. For more, see https://dagger.dev/unused-modules.
     */
    @Deprecated
    public Builder networkModule(NetworkModule networkModule) {
      Preconditions.checkNotNull(networkModule);
      return this;
    }

    /**
     * @deprecated This module is declared, but an instance is not used in the component. This method is a no-op. For more, see https://dagger.dev/unused-modules.
     */
    @Deprecated
    public Builder useCaseModule(UseCaseModule useCaseModule) {
      Preconditions.checkNotNull(useCaseModule);
      return this;
    }

    public PinPoIntApp_HiltComponents.SingletonC build() {
      Preconditions.checkBuilderRequirement(applicationContextModule, ApplicationContextModule.class);
      return new SingletonCImpl(applicationContextModule);
    }
  }

  private static final class ActivityRetainedCBuilder implements PinPoIntApp_HiltComponents.ActivityRetainedC.Builder {
    private final SingletonCImpl singletonCImpl;

    private ActivityRetainedCBuilder(SingletonCImpl singletonCImpl) {
      this.singletonCImpl = singletonCImpl;
    }

    @Override
    public PinPoIntApp_HiltComponents.ActivityRetainedC build() {
      return new ActivityRetainedCImpl(singletonCImpl);
    }
  }

  private static final class ActivityCBuilder implements PinPoIntApp_HiltComponents.ActivityC.Builder {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private Activity activity;

    private ActivityCBuilder(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
    }

    @Override
    public ActivityCBuilder activity(Activity activity) {
      this.activity = Preconditions.checkNotNull(activity);
      return this;
    }

    @Override
    public PinPoIntApp_HiltComponents.ActivityC build() {
      Preconditions.checkBuilderRequirement(activity, Activity.class);
      return new ActivityCImpl(singletonCImpl, activityRetainedCImpl, activity);
    }
  }

  private static final class FragmentCBuilder implements PinPoIntApp_HiltComponents.FragmentC.Builder {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private Fragment fragment;

    private FragmentCBuilder(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, ActivityCImpl activityCImpl) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;
    }

    @Override
    public FragmentCBuilder fragment(Fragment fragment) {
      this.fragment = Preconditions.checkNotNull(fragment);
      return this;
    }

    @Override
    public PinPoIntApp_HiltComponents.FragmentC build() {
      Preconditions.checkBuilderRequirement(fragment, Fragment.class);
      return new FragmentCImpl(singletonCImpl, activityRetainedCImpl, activityCImpl, fragment);
    }
  }

  private static final class ViewWithFragmentCBuilder implements PinPoIntApp_HiltComponents.ViewWithFragmentC.Builder {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private final FragmentCImpl fragmentCImpl;

    private View view;

    private ViewWithFragmentCBuilder(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, ActivityCImpl activityCImpl,
        FragmentCImpl fragmentCImpl) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;
      this.fragmentCImpl = fragmentCImpl;
    }

    @Override
    public ViewWithFragmentCBuilder view(View view) {
      this.view = Preconditions.checkNotNull(view);
      return this;
    }

    @Override
    public PinPoIntApp_HiltComponents.ViewWithFragmentC build() {
      Preconditions.checkBuilderRequirement(view, View.class);
      return new ViewWithFragmentCImpl(singletonCImpl, activityRetainedCImpl, activityCImpl, fragmentCImpl, view);
    }
  }

  private static final class ViewCBuilder implements PinPoIntApp_HiltComponents.ViewC.Builder {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private View view;

    private ViewCBuilder(SingletonCImpl singletonCImpl, ActivityRetainedCImpl activityRetainedCImpl,
        ActivityCImpl activityCImpl) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;
    }

    @Override
    public ViewCBuilder view(View view) {
      this.view = Preconditions.checkNotNull(view);
      return this;
    }

    @Override
    public PinPoIntApp_HiltComponents.ViewC build() {
      Preconditions.checkBuilderRequirement(view, View.class);
      return new ViewCImpl(singletonCImpl, activityRetainedCImpl, activityCImpl, view);
    }
  }

  private static final class ViewModelCBuilder implements PinPoIntApp_HiltComponents.ViewModelC.Builder {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private SavedStateHandle savedStateHandle;

    private ViewModelLifecycle viewModelLifecycle;

    private ViewModelCBuilder(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
    }

    @Override
    public ViewModelCBuilder savedStateHandle(SavedStateHandle handle) {
      this.savedStateHandle = Preconditions.checkNotNull(handle);
      return this;
    }

    @Override
    public ViewModelCBuilder viewModelLifecycle(ViewModelLifecycle viewModelLifecycle) {
      this.viewModelLifecycle = Preconditions.checkNotNull(viewModelLifecycle);
      return this;
    }

    @Override
    public PinPoIntApp_HiltComponents.ViewModelC build() {
      Preconditions.checkBuilderRequirement(savedStateHandle, SavedStateHandle.class);
      Preconditions.checkBuilderRequirement(viewModelLifecycle, ViewModelLifecycle.class);
      return new ViewModelCImpl(singletonCImpl, activityRetainedCImpl, savedStateHandle, viewModelLifecycle);
    }
  }

  private static final class ServiceCBuilder implements PinPoIntApp_HiltComponents.ServiceC.Builder {
    private final SingletonCImpl singletonCImpl;

    private Service service;

    private ServiceCBuilder(SingletonCImpl singletonCImpl) {
      this.singletonCImpl = singletonCImpl;
    }

    @Override
    public ServiceCBuilder service(Service service) {
      this.service = Preconditions.checkNotNull(service);
      return this;
    }

    @Override
    public PinPoIntApp_HiltComponents.ServiceC build() {
      Preconditions.checkBuilderRequirement(service, Service.class);
      return new ServiceCImpl(singletonCImpl, service);
    }
  }

  private static final class ViewWithFragmentCImpl extends PinPoIntApp_HiltComponents.ViewWithFragmentC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private final FragmentCImpl fragmentCImpl;

    private final ViewWithFragmentCImpl viewWithFragmentCImpl = this;

    private ViewWithFragmentCImpl(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, ActivityCImpl activityCImpl,
        FragmentCImpl fragmentCImpl, View viewParam) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;
      this.fragmentCImpl = fragmentCImpl;


    }
  }

  private static final class FragmentCImpl extends PinPoIntApp_HiltComponents.FragmentC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private final FragmentCImpl fragmentCImpl = this;

    private FragmentCImpl(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, ActivityCImpl activityCImpl,
        Fragment fragmentParam) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;


    }

    @Override
    public DefaultViewModelFactories.InternalFactoryFactory getHiltInternalFactoryFactory() {
      return activityCImpl.getHiltInternalFactoryFactory();
    }

    @Override
    public ViewWithFragmentComponentBuilder viewWithFragmentComponentBuilder() {
      return new ViewWithFragmentCBuilder(singletonCImpl, activityRetainedCImpl, activityCImpl, fragmentCImpl);
    }
  }

  private static final class ViewCImpl extends PinPoIntApp_HiltComponents.ViewC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private final ViewCImpl viewCImpl = this;

    private ViewCImpl(SingletonCImpl singletonCImpl, ActivityRetainedCImpl activityRetainedCImpl,
        ActivityCImpl activityCImpl, View viewParam) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;


    }
  }

  private static final class ActivityCImpl extends PinPoIntApp_HiltComponents.ActivityC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl = this;

    private ActivityCImpl(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, Activity activityParam) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;


    }

    @Override
    public void injectMainActivity(MainActivity mainActivity) {
    }

    @Override
    public DefaultViewModelFactories.InternalFactoryFactory getHiltInternalFactoryFactory() {
      return DefaultViewModelFactories_InternalFactoryFactory_Factory.newInstance(getViewModelKeys(), new ViewModelCBuilder(singletonCImpl, activityRetainedCImpl));
    }

    @Override
    public Set<String> getViewModelKeys() {
      return SetBuilder.<String>newSetBuilder(7).add(AuthViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(CourierLocationViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(IndoorMapViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(MainViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(OrderViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(PublicTrackingViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(RestaurantViewModel_HiltModules_KeyModule_ProvideFactory.provide()).build();
    }

    @Override
    public ViewModelComponentBuilder getViewModelComponentBuilder() {
      return new ViewModelCBuilder(singletonCImpl, activityRetainedCImpl);
    }

    @Override
    public FragmentComponentBuilder fragmentComponentBuilder() {
      return new FragmentCBuilder(singletonCImpl, activityRetainedCImpl, activityCImpl);
    }

    @Override
    public ViewComponentBuilder viewComponentBuilder() {
      return new ViewCBuilder(singletonCImpl, activityRetainedCImpl, activityCImpl);
    }
  }

  private static final class ViewModelCImpl extends PinPoIntApp_HiltComponents.ViewModelC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ViewModelCImpl viewModelCImpl = this;

    private Provider<AuthViewModel> authViewModelProvider;

    private Provider<CourierLocationViewModel> courierLocationViewModelProvider;

    private Provider<IndoorMapViewModel> indoorMapViewModelProvider;

    private Provider<MainViewModel> mainViewModelProvider;

    private Provider<OrderViewModel> orderViewModelProvider;

    private Provider<PublicTrackingViewModel> publicTrackingViewModelProvider;

    private Provider<RestaurantViewModel> restaurantViewModelProvider;

    private ViewModelCImpl(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, SavedStateHandle savedStateHandleParam,
        ViewModelLifecycle viewModelLifecycleParam) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;

      initialize(savedStateHandleParam, viewModelLifecycleParam);

    }

    @SuppressWarnings("unchecked")
    private void initialize(final SavedStateHandle savedStateHandleParam,
        final ViewModelLifecycle viewModelLifecycleParam) {
      this.authViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 0);
      this.courierLocationViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 1);
      this.indoorMapViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 2);
      this.mainViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 3);
      this.orderViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 4);
      this.publicTrackingViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 5);
      this.restaurantViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 6);
    }

    @Override
    public Map<String, Provider<ViewModel>> getHiltViewModelMap() {
      return MapBuilder.<String, Provider<ViewModel>>newMapBuilder(7).put("com.pinpoint.app.ui.auth.AuthViewModel", ((Provider) authViewModelProvider)).put("com.pinpoint.app.ui.location.CourierLocationViewModel", ((Provider) courierLocationViewModelProvider)).put("com.pinpoint.app.ui.indoor.IndoorMapViewModel", ((Provider) indoorMapViewModelProvider)).put("com.pinpoint.app.ui.MainViewModel", ((Provider) mainViewModelProvider)).put("com.pinpoint.app.ui.order.OrderViewModel", ((Provider) orderViewModelProvider)).put("com.pinpoint.app.ui.tracking.PublicTrackingViewModel", ((Provider) publicTrackingViewModelProvider)).put("com.pinpoint.app.ui.restaurant.RestaurantViewModel", ((Provider) restaurantViewModelProvider)).build();
    }

    private static final class SwitchingProvider<T> implements Provider<T> {
      private final SingletonCImpl singletonCImpl;

      private final ActivityRetainedCImpl activityRetainedCImpl;

      private final ViewModelCImpl viewModelCImpl;

      private final int id;

      SwitchingProvider(SingletonCImpl singletonCImpl, ActivityRetainedCImpl activityRetainedCImpl,
          ViewModelCImpl viewModelCImpl, int id) {
        this.singletonCImpl = singletonCImpl;
        this.activityRetainedCImpl = activityRetainedCImpl;
        this.viewModelCImpl = viewModelCImpl;
        this.id = id;
      }

      @SuppressWarnings("unchecked")
      @Override
      public T get() {
        switch (id) {
          case 0: // com.pinpoint.app.ui.auth.AuthViewModel 
          return (T) new AuthViewModel(singletonCImpl.bindBackendRepositoryProvider.get(), singletonCImpl.provideTokenManagerProvider.get());

          case 1: // com.pinpoint.app.ui.location.CourierLocationViewModel 
          return (T) new CourierLocationViewModel(singletonCImpl.bindBackendRepositoryProvider.get(), singletonCImpl.provideWebSocketManagerProvider.get(), singletonCImpl.provideFusedLocationProviderClientProvider.get());

          case 2: // com.pinpoint.app.ui.indoor.IndoorMapViewModel 
          return (T) new IndoorMapViewModel(singletonCImpl.bindBackendRepositoryProvider.get());

          case 3: // com.pinpoint.app.ui.MainViewModel 
          return (T) new MainViewModel(singletonCImpl.bindBuildingRepositoryProvider.get(), singletonCImpl.bindTrajectoryRepositoryProvider.get(), singletonCImpl.bindDeliverySessionRepositoryProvider.get(), singletonCImpl.provideComputeThermalProjectionUseCaseProvider.get(), singletonCImpl.provideGenerateThermalRouteAdviceUseCaseProvider.get(), singletonCImpl.provideGenerateAlertsUseCaseProvider.get(), singletonCImpl.providePredictivePinDropUseCaseProvider.get());

          case 4: // com.pinpoint.app.ui.order.OrderViewModel 
          return (T) new OrderViewModel(singletonCImpl.bindOrderRepositoryProvider.get());

          case 5: // com.pinpoint.app.ui.tracking.PublicTrackingViewModel 
          return (T) new PublicTrackingViewModel(singletonCImpl.bindBackendRepositoryProvider.get());

          case 6: // com.pinpoint.app.ui.restaurant.RestaurantViewModel 
          return (T) new RestaurantViewModel(singletonCImpl.bindBackendRepositoryProvider.get());

          default: throw new AssertionError(id);
        }
      }
    }
  }

  private static final class ActivityRetainedCImpl extends PinPoIntApp_HiltComponents.ActivityRetainedC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl = this;

    private Provider<ActivityRetainedLifecycle> provideActivityRetainedLifecycleProvider;

    private ActivityRetainedCImpl(SingletonCImpl singletonCImpl) {
      this.singletonCImpl = singletonCImpl;

      initialize();

    }

    @SuppressWarnings("unchecked")
    private void initialize() {
      this.provideActivityRetainedLifecycleProvider = DoubleCheck.provider(new SwitchingProvider<ActivityRetainedLifecycle>(singletonCImpl, activityRetainedCImpl, 0));
    }

    @Override
    public ActivityComponentBuilder activityComponentBuilder() {
      return new ActivityCBuilder(singletonCImpl, activityRetainedCImpl);
    }

    @Override
    public ActivityRetainedLifecycle getActivityRetainedLifecycle() {
      return provideActivityRetainedLifecycleProvider.get();
    }

    private static final class SwitchingProvider<T> implements Provider<T> {
      private final SingletonCImpl singletonCImpl;

      private final ActivityRetainedCImpl activityRetainedCImpl;

      private final int id;

      SwitchingProvider(SingletonCImpl singletonCImpl, ActivityRetainedCImpl activityRetainedCImpl,
          int id) {
        this.singletonCImpl = singletonCImpl;
        this.activityRetainedCImpl = activityRetainedCImpl;
        this.id = id;
      }

      @SuppressWarnings("unchecked")
      @Override
      public T get() {
        switch (id) {
          case 0: // dagger.hilt.android.ActivityRetainedLifecycle 
          return (T) ActivityRetainedComponentManager_LifecycleModule_ProvideActivityRetainedLifecycleFactory.provideActivityRetainedLifecycle();

          default: throw new AssertionError(id);
        }
      }
    }
  }

  private static final class ServiceCImpl extends PinPoIntApp_HiltComponents.ServiceC {
    private final SingletonCImpl singletonCImpl;

    private final ServiceCImpl serviceCImpl = this;

    private ServiceCImpl(SingletonCImpl singletonCImpl, Service serviceParam) {
      this.singletonCImpl = singletonCImpl;


    }

    @Override
    public void injectActivityRecognitionService(
        ActivityRecognitionService activityRecognitionService) {
    }

    @Override
    public void injectLocationTrackingService(LocationTrackingService locationTrackingService) {
      injectLocationTrackingService2(locationTrackingService);
    }

    @CanIgnoreReturnValue
    private LocationTrackingService injectLocationTrackingService2(
        LocationTrackingService instance) {
      LocationTrackingService_MembersInjector.injectActivityRecognitionManager(instance, singletonCImpl.transportActivityManagerProvider.get());
      LocationTrackingService_MembersInjector.injectTrajectoryRecorder(instance, singletonCImpl.trajectoryRecorderProvider.get());
      return instance;
    }
  }

  private static final class SingletonCImpl extends PinPoIntApp_HiltComponents.SingletonC {
    private final ApplicationContextModule applicationContextModule;

    private final SingletonCImpl singletonCImpl = this;

    private Provider<TokenManager> provideTokenManagerProvider;

    private Provider<OkHttpClient> provideOkHttpClientProvider;

    private Provider<Gson> provideGsonProvider;

    private Provider<BackendApi> provideBackendApiProvider;

    private Provider<BackendRepositoryImpl> backendRepositoryImplProvider;

    private Provider<BackendRepository> bindBackendRepositoryProvider;

    private Provider<WebSocketManager> provideWebSocketManagerProvider;

    private Provider<FusedLocationProviderClient> provideFusedLocationProviderClientProvider;

    private Provider<PinPoIntDatabase> provideDatabaseProvider;

    private Provider<BuildingRepositoryImpl> buildingRepositoryImplProvider;

    private Provider<BuildingRepository> bindBuildingRepositoryProvider;

    private Provider<TrajectoryRepositoryImpl> trajectoryRepositoryImplProvider;

    private Provider<TrajectoryRepository> bindTrajectoryRepositoryProvider;

    private Provider<DeliverySessionRepositoryImpl> deliverySessionRepositoryImplProvider;

    private Provider<DeliverySessionRepository> bindDeliverySessionRepositoryProvider;

    private Provider<ComputeThermalProjectionUseCase> provideComputeThermalProjectionUseCaseProvider;

    private Provider<ComputeBuildingDifficultyUseCase> provideComputeBuildingDifficultyUseCaseProvider;

    private Provider<GenerateThermalRouteAdviceUseCase> provideGenerateThermalRouteAdviceUseCaseProvider;

    private Provider<GenerateAlertsUseCase> provideGenerateAlertsUseCaseProvider;

    private Provider<BackendRemoteDataSource> provideBackendRemoteDataSourceProvider;

    private Provider<PredictivePinDropUseCase> providePredictivePinDropUseCaseProvider;

    private Provider<OrderRepositoryImpl> orderRepositoryImplProvider;

    private Provider<OrderRepository> bindOrderRepositoryProvider;

    private Provider<TransportActivityManager> transportActivityManagerProvider;

    private Provider<TrajectoryRecorder> trajectoryRecorderProvider;

    private SingletonCImpl(ApplicationContextModule applicationContextModuleParam) {
      this.applicationContextModule = applicationContextModuleParam;
      initialize(applicationContextModuleParam);

    }

    private BuildingDao buildingDao() {
      return DatabaseModule_ProvideBuildingDaoFactory.provideBuildingDao(provideDatabaseProvider.get());
    }

    private TrajectoryDao trajectoryDao() {
      return DatabaseModule_ProvideTrajectoryDaoFactory.provideTrajectoryDao(provideDatabaseProvider.get());
    }

    private DeliverySessionDao deliverySessionDao() {
      return DatabaseModule_ProvideDeliverySessionDaoFactory.provideDeliverySessionDao(provideDatabaseProvider.get());
    }

    @SuppressWarnings("unchecked")
    private void initialize(final ApplicationContextModule applicationContextModuleParam) {
      this.provideTokenManagerProvider = DoubleCheck.provider(new SwitchingProvider<TokenManager>(singletonCImpl, 3));
      this.provideOkHttpClientProvider = DoubleCheck.provider(new SwitchingProvider<OkHttpClient>(singletonCImpl, 2));
      this.provideGsonProvider = DoubleCheck.provider(new SwitchingProvider<Gson>(singletonCImpl, 4));
      this.provideBackendApiProvider = DoubleCheck.provider(new SwitchingProvider<BackendApi>(singletonCImpl, 1));
      this.backendRepositoryImplProvider = new SwitchingProvider<>(singletonCImpl, 0);
      this.bindBackendRepositoryProvider = DoubleCheck.provider((Provider) backendRepositoryImplProvider);
      this.provideWebSocketManagerProvider = DoubleCheck.provider(new SwitchingProvider<WebSocketManager>(singletonCImpl, 5));
      this.provideFusedLocationProviderClientProvider = DoubleCheck.provider(new SwitchingProvider<FusedLocationProviderClient>(singletonCImpl, 6));
      this.provideDatabaseProvider = DoubleCheck.provider(new SwitchingProvider<PinPoIntDatabase>(singletonCImpl, 8));
      this.buildingRepositoryImplProvider = new SwitchingProvider<>(singletonCImpl, 7);
      this.bindBuildingRepositoryProvider = DoubleCheck.provider((Provider) buildingRepositoryImplProvider);
      this.trajectoryRepositoryImplProvider = new SwitchingProvider<>(singletonCImpl, 9);
      this.bindTrajectoryRepositoryProvider = DoubleCheck.provider((Provider) trajectoryRepositoryImplProvider);
      this.deliverySessionRepositoryImplProvider = new SwitchingProvider<>(singletonCImpl, 10);
      this.bindDeliverySessionRepositoryProvider = DoubleCheck.provider((Provider) deliverySessionRepositoryImplProvider);
      this.provideComputeThermalProjectionUseCaseProvider = DoubleCheck.provider(new SwitchingProvider<ComputeThermalProjectionUseCase>(singletonCImpl, 11));
      this.provideComputeBuildingDifficultyUseCaseProvider = DoubleCheck.provider(new SwitchingProvider<ComputeBuildingDifficultyUseCase>(singletonCImpl, 13));
      this.provideGenerateThermalRouteAdviceUseCaseProvider = DoubleCheck.provider(new SwitchingProvider<GenerateThermalRouteAdviceUseCase>(singletonCImpl, 12));
      this.provideGenerateAlertsUseCaseProvider = DoubleCheck.provider(new SwitchingProvider<GenerateAlertsUseCase>(singletonCImpl, 14));
      this.provideBackendRemoteDataSourceProvider = DoubleCheck.provider(new SwitchingProvider<BackendRemoteDataSource>(singletonCImpl, 16));
      this.providePredictivePinDropUseCaseProvider = DoubleCheck.provider(new SwitchingProvider<PredictivePinDropUseCase>(singletonCImpl, 15));
      this.orderRepositoryImplProvider = new SwitchingProvider<>(singletonCImpl, 17);
      this.bindOrderRepositoryProvider = DoubleCheck.provider((Provider) orderRepositoryImplProvider);
      this.transportActivityManagerProvider = DoubleCheck.provider(new SwitchingProvider<TransportActivityManager>(singletonCImpl, 18));
      this.trajectoryRecorderProvider = DoubleCheck.provider(new SwitchingProvider<TrajectoryRecorder>(singletonCImpl, 19));
    }

    @Override
    public void injectPinPoIntApp(PinPoIntApp pinPoIntApp) {
    }

    @Override
    public Set<Boolean> getDisableFragmentGetContextFix() {
      return Collections.<Boolean>emptySet();
    }

    @Override
    public ActivityRetainedComponentBuilder retainedComponentBuilder() {
      return new ActivityRetainedCBuilder(singletonCImpl);
    }

    @Override
    public ServiceComponentBuilder serviceComponentBuilder() {
      return new ServiceCBuilder(singletonCImpl);
    }

    private static final class SwitchingProvider<T> implements Provider<T> {
      private final SingletonCImpl singletonCImpl;

      private final int id;

      SwitchingProvider(SingletonCImpl singletonCImpl, int id) {
        this.singletonCImpl = singletonCImpl;
        this.id = id;
      }

      @SuppressWarnings("unchecked")
      @Override
      public T get() {
        switch (id) {
          case 0: // com.pinpoint.app.data.repository.BackendRepositoryImpl 
          return (T) new BackendRepositoryImpl(singletonCImpl.provideBackendApiProvider.get());

          case 1: // com.pinpoint.app.data.remote.backend.BackendApi 
          return (T) NetworkModule_ProvideBackendApiFactory.provideBackendApi(singletonCImpl.provideOkHttpClientProvider.get(), singletonCImpl.provideGsonProvider.get());

          case 2: // okhttp3.OkHttpClient 
          return (T) NetworkModule_ProvideOkHttpClientFactory.provideOkHttpClient(singletonCImpl.provideTokenManagerProvider.get());

          case 3: // com.pinpoint.app.data.TokenManager 
          return (T) DataModule_ProvideTokenManagerFactory.provideTokenManager(ApplicationContextModule_ProvideContextFactory.provideContext(singletonCImpl.applicationContextModule));

          case 4: // com.google.gson.Gson 
          return (T) NetworkModule_ProvideGsonFactory.provideGson();

          case 5: // com.pinpoint.app.data.websocket.WebSocketManager 
          return (T) NetworkModule_ProvideWebSocketManagerFactory.provideWebSocketManager(singletonCImpl.provideOkHttpClientProvider.get(), singletonCImpl.provideGsonProvider.get());

          case 6: // com.google.android.gms.location.FusedLocationProviderClient 
          return (T) NetworkModule_ProvideFusedLocationProviderClientFactory.provideFusedLocationProviderClient(ApplicationContextModule_ProvideContextFactory.provideContext(singletonCImpl.applicationContextModule));

          case 7: // com.pinpoint.app.data.repository.BuildingRepositoryImpl 
          return (T) new BuildingRepositoryImpl(singletonCImpl.buildingDao(), singletonCImpl.provideBackendApiProvider.get());

          case 8: // com.pinpoint.app.data.local.PinPoIntDatabase 
          return (T) DatabaseModule_ProvideDatabaseFactory.provideDatabase(ApplicationContextModule_ProvideContextFactory.provideContext(singletonCImpl.applicationContextModule));

          case 9: // com.pinpoint.app.data.repository.TrajectoryRepositoryImpl 
          return (T) new TrajectoryRepositoryImpl(singletonCImpl.trajectoryDao(), singletonCImpl.provideBackendApiProvider.get());

          case 10: // com.pinpoint.app.data.repository.DeliverySessionRepositoryImpl 
          return (T) new DeliverySessionRepositoryImpl(singletonCImpl.deliverySessionDao());

          case 11: // com.pinpoint.app.domain.usecase.ComputeThermalProjectionUseCase 
          return (T) UseCaseModule_ProvideComputeThermalProjectionUseCaseFactory.provideComputeThermalProjectionUseCase();

          case 12: // com.pinpoint.app.domain.usecase.GenerateThermalRouteAdviceUseCase 
          return (T) UseCaseModule_ProvideGenerateThermalRouteAdviceUseCaseFactory.provideGenerateThermalRouteAdviceUseCase(singletonCImpl.provideComputeBuildingDifficultyUseCaseProvider.get());

          case 13: // com.pinpoint.app.domain.usecase.ComputeBuildingDifficultyUseCase 
          return (T) UseCaseModule_ProvideComputeBuildingDifficultyUseCaseFactory.provideComputeBuildingDifficultyUseCase();

          case 14: // com.pinpoint.app.domain.usecase.GenerateAlertsUseCase 
          return (T) UseCaseModule_ProvideGenerateAlertsUseCaseFactory.provideGenerateAlertsUseCase();

          case 15: // com.pinpoint.app.domain.usecase.PredictivePinDropUseCase 
          return (T) UseCaseModule_ProvidePredictivePinDropUseCaseFactory.providePredictivePinDropUseCase(singletonCImpl.provideBackendRemoteDataSourceProvider.get());

          case 16: // com.pinpoint.app.data.remote.backend.BackendRemoteDataSource 
          return (T) NetworkModule_ProvideBackendRemoteDataSourceFactory.provideBackendRemoteDataSource(singletonCImpl.provideBackendApiProvider.get());

          case 17: // com.pinpoint.app.data.repository.OrderRepositoryImpl 
          return (T) new OrderRepositoryImpl(singletonCImpl.provideBackendApiProvider.get());

          case 18: // com.pinpoint.app.service.TransportActivityManager 
          return (T) new TransportActivityManager(ApplicationContextModule_ProvideContextFactory.provideContext(singletonCImpl.applicationContextModule));

          case 19: // com.pinpoint.app.service.TrajectoryRecorder 
          return (T) new TrajectoryRecorder(singletonCImpl.bindTrajectoryRepositoryProvider.get());

          default: throw new AssertionError(id);
        }
      }
    }
  }
}
