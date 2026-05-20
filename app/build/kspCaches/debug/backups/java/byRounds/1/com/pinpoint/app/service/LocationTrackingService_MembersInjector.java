package com.pinpoint.app.service;

import dagger.MembersInjector;
import dagger.internal.DaggerGenerated;
import dagger.internal.InjectedFieldSignature;
import dagger.internal.QualifierMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

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
public final class LocationTrackingService_MembersInjector implements MembersInjector<LocationTrackingService> {
  private final Provider<TransportActivityManager> activityRecognitionManagerProvider;

  private final Provider<TrajectoryRecorder> trajectoryRecorderProvider;

  public LocationTrackingService_MembersInjector(
      Provider<TransportActivityManager> activityRecognitionManagerProvider,
      Provider<TrajectoryRecorder> trajectoryRecorderProvider) {
    this.activityRecognitionManagerProvider = activityRecognitionManagerProvider;
    this.trajectoryRecorderProvider = trajectoryRecorderProvider;
  }

  public static MembersInjector<LocationTrackingService> create(
      Provider<TransportActivityManager> activityRecognitionManagerProvider,
      Provider<TrajectoryRecorder> trajectoryRecorderProvider) {
    return new LocationTrackingService_MembersInjector(activityRecognitionManagerProvider, trajectoryRecorderProvider);
  }

  @Override
  public void injectMembers(LocationTrackingService instance) {
    injectActivityRecognitionManager(instance, activityRecognitionManagerProvider.get());
    injectTrajectoryRecorder(instance, trajectoryRecorderProvider.get());
  }

  @InjectedFieldSignature("com.pinpoint.app.service.LocationTrackingService.activityRecognitionManager")
  public static void injectActivityRecognitionManager(LocationTrackingService instance,
      TransportActivityManager activityRecognitionManager) {
    instance.activityRecognitionManager = activityRecognitionManager;
  }

  @InjectedFieldSignature("com.pinpoint.app.service.LocationTrackingService.trajectoryRecorder")
  public static void injectTrajectoryRecorder(LocationTrackingService instance,
      TrajectoryRecorder trajectoryRecorder) {
    instance.trajectoryRecorder = trajectoryRecorder;
  }
}
