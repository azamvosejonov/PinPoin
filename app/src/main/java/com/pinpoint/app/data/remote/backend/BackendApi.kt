package com.pinpoint.app.data.remote.backend

import com.pinpoint.app.data.remote.backend.dto.AlertResponseDto
import com.pinpoint.app.data.remote.backend.dto.BuildingDto
import com.pinpoint.app.data.remote.backend.dto.BuildingUpsertRequest
import com.pinpoint.app.data.remote.backend.dto.PredictivePinRequestDto
import com.pinpoint.app.data.remote.backend.dto.PredictivePinResponseDto
import com.pinpoint.app.data.remote.backend.dto.ThermalProjectionRequestDto
import com.pinpoint.app.data.remote.backend.dto.ThermalProjectionResponseDto
import com.pinpoint.app.data.remote.backend.dto.SyncResponseDto
import com.pinpoint.app.data.remote.backend.dto.TrajectoryCreateRequest
import com.pinpoint.app.data.remote.backend.dto.DomofonValidationRequestDto
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

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
}
