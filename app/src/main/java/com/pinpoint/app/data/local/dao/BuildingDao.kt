package com.pinpoint.app.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction
import androidx.room.Update
import com.pinpoint.app.data.local.entity.BuildingEntity
import com.pinpoint.app.data.local.entity.EntranceEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface BuildingDao {

    @Query("SELECT * FROM buildings WHERE building_external_id = :externalId LIMIT 1")
    fun observeBuildingByExternalId(externalId: String): Flow<BuildingEntity?>

    @Query("SELECT * FROM buildings WHERE building_external_id = :externalId LIMIT 1")
    suspend fun getBuildingByExternalId(externalId: String): BuildingEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertBuilding(buildingEntity: BuildingEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertEntrances(entrances: List<EntranceEntity>)

    @Query("SELECT * FROM entrances WHERE building_id = :buildingId")
    fun observeEntrancesByBuilding(buildingId: Long): Flow<List<EntranceEntity>>

    @Query("SELECT * FROM entrances WHERE id = :entranceId LIMIT 1")
    suspend fun getEntranceById(entranceId: Long): EntranceEntity?

    @Query("UPDATE entrances SET validated_count = CASE WHEN validated_count > 0 THEN validated_count - 1 ELSE 0 END WHERE id = :entranceId")
    suspend fun markDomofonFailure(entranceId: Long)

    @Transaction
    suspend fun upsertBuildingWithEntrances(
        building: BuildingEntity,
        entrances: List<EntranceEntity>
    ) {
        val buildingId = upsertBuilding(building)
        val enrichedEntrances = entrances.map { it.copy(buildingId = buildingId) }
        upsertEntrances(enrichedEntrances)
    }

    @Query("UPDATE entrances SET domofon_code = :code, validated_count = validated_count + 1, last_validated_at = :timestamp WHERE id = :entranceId")
    suspend fun updateDomofonCode(entranceId: Long, code: String, timestamp: Long)

    @Query("SELECT * FROM entrances WHERE building_id = :buildingId ORDER BY validated_count DESC")
    suspend fun getEntrancesForBuilding(buildingId: Long): List<EntranceEntity>
}
