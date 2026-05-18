package com.pinpoint.app.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.pinpoint.app.data.local.entity.TrajectoryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface TrajectoryDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTrajectory(trajectory: TrajectoryEntity)

    @Query("SELECT * FROM trajectories WHERE building_external_id = :buildingId ORDER BY delivered_at DESC LIMIT :limit")
    suspend fun getRecentTrajectories(buildingId: String, limit: Int = 20): List<TrajectoryEntity>

    @Query("SELECT * FROM trajectories WHERE courier_id = :courierId ORDER BY delivered_at DESC LIMIT :limit")
    fun observeTrajectoriesForCourier(courierId: String, limit: Int = 50): Flow<List<TrajectoryEntity>>
}
