package com.pinpoint.app.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.pinpoint.app.data.local.dao.BuildingDao
import com.pinpoint.app.data.local.dao.DeliverySessionDao
import com.pinpoint.app.data.local.dao.TrajectoryDao
import com.pinpoint.app.data.local.entity.BuildingEntity
import com.pinpoint.app.data.local.entity.DeliverySessionEntity
import com.pinpoint.app.data.local.entity.EntranceEntity
import com.pinpoint.app.data.local.entity.TrajectoryEntity

@Database(
    entities = [
        BuildingEntity::class,
        EntranceEntity::class,
        TrajectoryEntity::class,
        DeliverySessionEntity::class
    ],
    version = 1,
    exportSchema = true
)
@TypeConverters(value = [PointListConverter::class])
abstract class PinPoIntDatabase : RoomDatabase() {
    abstract fun buildingDao(): BuildingDao
    abstract fun trajectoryDao(): TrajectoryDao
    abstract fun deliverySessionDao(): DeliverySessionDao
}
