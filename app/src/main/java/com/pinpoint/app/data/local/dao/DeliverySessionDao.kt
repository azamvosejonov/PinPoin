package com.pinpoint.app.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.pinpoint.app.data.local.entity.DeliverySessionEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface DeliverySessionDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSession(session: DeliverySessionEntity): Long

    @Update
    suspend fun updateSession(session: DeliverySessionEntity)

    @Query("SELECT * FROM delivery_sessions WHERE order_id = :orderId LIMIT 1")
    suspend fun getSessionByOrderId(orderId: String): DeliverySessionEntity?

    @Query("SELECT * FROM delivery_sessions WHERE courier_id = :courierId ORDER BY start_time DESC LIMIT 1")
    fun observeLatestSession(courierId: String): Flow<DeliverySessionEntity?>
}
