package com.pinpoint.app.data.remote.backend

import com.pinpoint.app.data.remote.backend.dto.BuildingDto
import com.pinpoint.app.data.remote.backend.dto.BuildingUpsertRequest
import com.pinpoint.app.data.remote.backend.dto.PredictivePinRequestDto
import com.pinpoint.app.data.remote.backend.dto.PredictivePinResponseDto
import com.pinpoint.app.data.remote.backend.dto.ThermalProjectionRequestDto
import com.pinpoint.app.data.remote.backend.dto.ThermalProjectionResponseDto
import javax.inject.Inject

class BackendRemoteDataSource @Inject constructor(
    private val api: BackendApi
) {

    suspend fun predictivePin(request: PredictivePinRequestDto): PredictivePinResponseDto = api.predictivePin(request)

    suspend fun thermalProjection(request: ThermalProjectionRequestDto): ThermalProjectionResponseDto = api.thermalProjection(request)

    suspend fun upsertBuilding(request: BuildingUpsertRequest): BuildingDto = api.upsertBuilding(request)

    suspend fun getBuilding(externalId: String): BuildingDto = api.getBuilding(externalId)
}
