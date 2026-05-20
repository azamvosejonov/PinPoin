package com.pinpoint.app.data.remote.backend

import com.pinpoint.app.data.remote.backend.dto.BuildingDto
import com.pinpoint.app.data.remote.backend.dto.BuildingUpsertRequest
import com.pinpoint.app.data.remote.backend.dto.PredictivePinRequestDto
import com.pinpoint.app.data.remote.backend.dto.PredictivePinResponseDto
import com.pinpoint.app.data.remote.backend.dto.ThermalProjectionRequestDto
import com.pinpoint.app.data.remote.backend.dto.ThermalProjectionResponseDto
import com.pinpoint.app.data.remote.backend.dto.SyncResponseDto
import com.pinpoint.app.data.remote.backend.dto.TrajectoryCreateRequest
import com.pinpoint.app.data.remote.backend.dto.DomofonValidationRequestDto
import com.pinpoint.app.data.remote.backend.dto.OrderDto
import com.pinpoint.app.data.remote.backend.dto.OrderStatusUpdateDto
import com.pinpoint.app.data.remote.backend.dto.OrderDeclineDto
import com.pinpoint.app.data.remote.backend.dto.CourierStatusDto
import com.pinpoint.app.data.remote.backend.dto.CourierStatusUpdateDto
import com.pinpoint.app.data.remote.backend.dto.CourierCashCollectDto
import com.pinpoint.app.data.remote.backend.dto.CourierLocationDto
import com.pinpoint.app.data.remote.backend.dto.CourierLocationUpdateDto
import com.pinpoint.app.data.remote.backend.dto.RestaurantDto
import com.pinpoint.app.data.remote.backend.dto.IndoorMapDto
import com.pinpoint.app.data.remote.backend.dto.IndoorPathCreateDto
import com.pinpoint.app.data.remote.backend.dto.IndoorPathDetailDto
import com.pinpoint.app.data.remote.backend.dto.TelemetryDto
import com.pinpoint.app.data.remote.backend.dto.PinCorrectionRequestDto
import com.pinpoint.app.data.remote.backend.dto.PinCorrectionResponseDto
import com.pinpoint.app.data.remote.backend.dto.AuthRegisterDto
import com.pinpoint.app.data.remote.backend.dto.AuthLoginDto
import com.pinpoint.app.data.remote.backend.dto.TokenPairDto
import com.pinpoint.app.data.remote.backend.dto.UserDto
import com.pinpoint.app.data.remote.backend.dto.OrderTrackingDto
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

interface BackendApi {

    @POST("predictive-pin")
    suspend fun predictivePin(@Body body: PredictivePinRequestDto): PredictivePinResponseDto

    @POST("thermal-projection")
    suspend fun thermalProjection(@Body body: ThermalProjectionRequestDto): ThermalProjectionResponseDto

    @POST("buildings")
    suspend fun upsertBuilding(@Body body: BuildingUpsertRequest): BuildingDto

    @GET("buildings/{externalId}")
    suspend fun getBuilding(@Path("externalId") externalId: String): BuildingDto

    @POST("buildings/{externalId}/trajectories")
    suspend fun submitTrajectory(
        @Path("externalId") externalId: String,
        @Body body: TrajectoryCreateRequest
    ): SyncResponseDto

    @POST("entrances/{entranceId}/domofon")
    suspend fun validateDomofon(
        @Path("entranceId") entranceId: Long,
        @Body body: DomofonValidationRequestDto
    ): com.pinpoint.app.data.remote.backend.dto.EntranceDto

    // Order endpoints
    @GET("orders/my")
    suspend fun getMyOrders(): List<OrderDto>

    @GET("orders/{orderId}")
    suspend fun getOrder(@Path("orderId") orderId: Int): OrderDto

    @PUT("orders/{orderId}/status")
    suspend fun updateOrderStatus(
        @Path("orderId") orderId: Int,
        @Body body: OrderStatusUpdateDto
    ): OrderDto

    @POST("orders/{orderId}/decline")
    suspend fun declineOrder(
        @Path("orderId") orderId: Int,
        @Body body: OrderDeclineDto
    ): OrderDto

    // Courier status endpoints
    @POST("courier/status")
    suspend fun updateCourierStatus(@Body body: CourierStatusUpdateDto): CourierStatusDto

    @GET("courier/status")
    suspend fun getCourierStatus(@Query("courier_id") courierId: Int): CourierStatusDto

    @POST("courier/{courierId}/collect-cash")
    suspend fun collectCash(
        @Path("courierId") courierId: Int,
        @Body body: CourierCashCollectDto
    ): CourierStatusDto

    // Auth endpoints
    @POST("auth/register")
    suspend fun register(@Body body: AuthRegisterDto): UserDto

    @POST("auth/token")
    suspend fun login(@Body body: AuthLoginDto): TokenPairDto

    @POST("auth/refresh")
    suspend fun refreshToken(@Body body: TokenPairDto): TokenPairDto

    @POST("auth/logout")
    suspend fun logout(@Body body: TokenPairDto)

    @GET("auth/me")
    suspend fun getMe(): UserDto

    // Courier location endpoints
    @POST("courier/location")
    suspend fun updateLocation(@Body body: CourierLocationUpdateDto): CourierLocationDto

    @GET("courier/{courierId}/location")
    suspend fun getCourierLocation(@Path("courierId") courierId: Int): CourierLocationDto

    // Restaurant endpoints
    @GET("restaurants")
    suspend fun getRestaurants(): List<RestaurantDto>

    @GET("restaurants/{restaurantId}")
    suspend fun getRestaurant(@Path("restaurantId") restaurantId: Int): RestaurantDto

    // Indoor map endpoints
    @GET("buildings/{externalId}/indoor-map")
    suspend fun getIndoorMap(
        @Path("externalId") externalId: String,
        @Query("entrance") entrance: Int,
        @Query("floor") floor: Int
    ): IndoorMapDto

    @POST("buildings/{externalId}/indoor-paths")
    suspend fun createIndoorPath(
        @Path("externalId") externalId: String,
        @Body body: IndoorPathCreateDto
    ): IndoorPathDetailDto

    @POST("buildings/{externalId}/telemetry")
    suspend fun submitTelemetry(
        @Path("externalId") externalId: String,
        @Body body: TelemetryDto
    ): SyncResponseDto

    // Indoor timing
    @POST("orders/{orderId}/indoor-enter")
    suspend fun markIndoorEnter(@Path("orderId") orderId: Int): Map<String, Any>

    @POST("orders/{orderId}/indoor-exit")
    suspend fun markIndoorExit(@Path("orderId") orderId: Int): Map<String, Any>

    // Pin correction
    @POST("orders/{orderId}/correct-pin")
    suspend fun correctPin(
        @Path("orderId") orderId: Int,
        @Body body: PinCorrectionRequestDto
    ): PinCorrectionResponseDto

    // Public tracking
    @GET("public/tracking/{trackingHash}")
    suspend fun getPublicTracking(@Path("trackingHash") trackingHash: String): OrderTrackingDto
}
