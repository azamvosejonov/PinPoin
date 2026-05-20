package com.pinpoint.app.data.local;

import androidx.annotation.NonNull;
import androidx.room.DatabaseConfiguration;
import androidx.room.InvalidationTracker;
import androidx.room.RoomDatabase;
import androidx.room.RoomOpenHelper;
import androidx.room.migration.AutoMigrationSpec;
import androidx.room.migration.Migration;
import androidx.room.util.DBUtil;
import androidx.room.util.TableInfo;
import androidx.sqlite.db.SupportSQLiteDatabase;
import androidx.sqlite.db.SupportSQLiteOpenHelper;
import com.pinpoint.app.data.local.dao.BuildingDao;
import com.pinpoint.app.data.local.dao.BuildingDao_Impl;
import com.pinpoint.app.data.local.dao.DeliverySessionDao;
import com.pinpoint.app.data.local.dao.DeliverySessionDao_Impl;
import com.pinpoint.app.data.local.dao.TrajectoryDao;
import com.pinpoint.app.data.local.dao.TrajectoryDao_Impl;
import java.lang.Class;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.annotation.processing.Generated;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class PinPoIntDatabase_Impl extends PinPoIntDatabase {
  private volatile BuildingDao _buildingDao;

  private volatile TrajectoryDao _trajectoryDao;

  private volatile DeliverySessionDao _deliverySessionDao;

  @Override
  @NonNull
  protected SupportSQLiteOpenHelper createOpenHelper(@NonNull final DatabaseConfiguration config) {
    final SupportSQLiteOpenHelper.Callback _openCallback = new RoomOpenHelper(config, new RoomOpenHelper.Delegate(1) {
      @Override
      public void createAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("CREATE TABLE IF NOT EXISTS `buildings` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `building_external_id` TEXT NOT NULL, `address` TEXT NOT NULL, `latitude` REAL NOT NULL, `longitude` REAL NOT NULL, `building_type` TEXT NOT NULL, `difficulty_index` INTEGER NOT NULL, `has_lift` INTEGER NOT NULL, `requires_chip` INTEGER NOT NULL, `entrance_hint` TEXT, `updated_at` INTEGER NOT NULL)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `entrances` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `building_id` INTEGER NOT NULL, `label` TEXT NOT NULL, `latitude` REAL NOT NULL, `longitude` REAL NOT NULL, `domofon_code` TEXT, `has_barrier` INTEGER NOT NULL, `validated_count` INTEGER NOT NULL, `last_validated_at` INTEGER NOT NULL, FOREIGN KEY(`building_id`) REFERENCES `buildings`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_entrances_building_id` ON `entrances` (`building_id`)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `trajectories` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `building_external_id` TEXT NOT NULL, `courier_id` TEXT NOT NULL, `delivered_at` INTEGER NOT NULL, `data_points` TEXT NOT NULL)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `delivery_sessions` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `order_id` TEXT NOT NULL, `courier_id` TEXT NOT NULL, `building_external_id` TEXT NOT NULL, `start_time` INTEGER NOT NULL, `end_time` INTEGER, `temperature_model` TEXT NOT NULL, `start_temperature` REAL NOT NULL, `predicted_temperature` REAL NOT NULL, `predicted_eta` INTEGER NOT NULL, `transport_mode` TEXT)");
        db.execSQL("CREATE TABLE IF NOT EXISTS room_master_table (id INTEGER PRIMARY KEY,identity_hash TEXT)");
        db.execSQL("INSERT OR REPLACE INTO room_master_table (id,identity_hash) VALUES(42, 'c337ff5a1f29a73634efb6613f605a2b')");
      }

      @Override
      public void dropAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("DROP TABLE IF EXISTS `buildings`");
        db.execSQL("DROP TABLE IF EXISTS `entrances`");
        db.execSQL("DROP TABLE IF EXISTS `trajectories`");
        db.execSQL("DROP TABLE IF EXISTS `delivery_sessions`");
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onDestructiveMigration(db);
          }
        }
      }

      @Override
      public void onCreate(@NonNull final SupportSQLiteDatabase db) {
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onCreate(db);
          }
        }
      }

      @Override
      public void onOpen(@NonNull final SupportSQLiteDatabase db) {
        mDatabase = db;
        db.execSQL("PRAGMA foreign_keys = ON");
        internalInitInvalidationTracker(db);
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onOpen(db);
          }
        }
      }

      @Override
      public void onPreMigrate(@NonNull final SupportSQLiteDatabase db) {
        DBUtil.dropFtsSyncTriggers(db);
      }

      @Override
      public void onPostMigrate(@NonNull final SupportSQLiteDatabase db) {
      }

      @Override
      @NonNull
      public RoomOpenHelper.ValidationResult onValidateSchema(
          @NonNull final SupportSQLiteDatabase db) {
        final HashMap<String, TableInfo.Column> _columnsBuildings = new HashMap<String, TableInfo.Column>(11);
        _columnsBuildings.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsBuildings.put("building_external_id", new TableInfo.Column("building_external_id", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsBuildings.put("address", new TableInfo.Column("address", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsBuildings.put("latitude", new TableInfo.Column("latitude", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsBuildings.put("longitude", new TableInfo.Column("longitude", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsBuildings.put("building_type", new TableInfo.Column("building_type", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsBuildings.put("difficulty_index", new TableInfo.Column("difficulty_index", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsBuildings.put("has_lift", new TableInfo.Column("has_lift", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsBuildings.put("requires_chip", new TableInfo.Column("requires_chip", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsBuildings.put("entrance_hint", new TableInfo.Column("entrance_hint", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsBuildings.put("updated_at", new TableInfo.Column("updated_at", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysBuildings = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesBuildings = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoBuildings = new TableInfo("buildings", _columnsBuildings, _foreignKeysBuildings, _indicesBuildings);
        final TableInfo _existingBuildings = TableInfo.read(db, "buildings");
        if (!_infoBuildings.equals(_existingBuildings)) {
          return new RoomOpenHelper.ValidationResult(false, "buildings(com.pinpoint.app.data.local.entity.BuildingEntity).\n"
                  + " Expected:\n" + _infoBuildings + "\n"
                  + " Found:\n" + _existingBuildings);
        }
        final HashMap<String, TableInfo.Column> _columnsEntrances = new HashMap<String, TableInfo.Column>(9);
        _columnsEntrances.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEntrances.put("building_id", new TableInfo.Column("building_id", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEntrances.put("label", new TableInfo.Column("label", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEntrances.put("latitude", new TableInfo.Column("latitude", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEntrances.put("longitude", new TableInfo.Column("longitude", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEntrances.put("domofon_code", new TableInfo.Column("domofon_code", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEntrances.put("has_barrier", new TableInfo.Column("has_barrier", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEntrances.put("validated_count", new TableInfo.Column("validated_count", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEntrances.put("last_validated_at", new TableInfo.Column("last_validated_at", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysEntrances = new HashSet<TableInfo.ForeignKey>(1);
        _foreignKeysEntrances.add(new TableInfo.ForeignKey("buildings", "CASCADE", "NO ACTION", Arrays.asList("building_id"), Arrays.asList("id")));
        final HashSet<TableInfo.Index> _indicesEntrances = new HashSet<TableInfo.Index>(1);
        _indicesEntrances.add(new TableInfo.Index("index_entrances_building_id", false, Arrays.asList("building_id"), Arrays.asList("ASC")));
        final TableInfo _infoEntrances = new TableInfo("entrances", _columnsEntrances, _foreignKeysEntrances, _indicesEntrances);
        final TableInfo _existingEntrances = TableInfo.read(db, "entrances");
        if (!_infoEntrances.equals(_existingEntrances)) {
          return new RoomOpenHelper.ValidationResult(false, "entrances(com.pinpoint.app.data.local.entity.EntranceEntity).\n"
                  + " Expected:\n" + _infoEntrances + "\n"
                  + " Found:\n" + _existingEntrances);
        }
        final HashMap<String, TableInfo.Column> _columnsTrajectories = new HashMap<String, TableInfo.Column>(5);
        _columnsTrajectories.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrajectories.put("building_external_id", new TableInfo.Column("building_external_id", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrajectories.put("courier_id", new TableInfo.Column("courier_id", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrajectories.put("delivered_at", new TableInfo.Column("delivered_at", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrajectories.put("data_points", new TableInfo.Column("data_points", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysTrajectories = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesTrajectories = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoTrajectories = new TableInfo("trajectories", _columnsTrajectories, _foreignKeysTrajectories, _indicesTrajectories);
        final TableInfo _existingTrajectories = TableInfo.read(db, "trajectories");
        if (!_infoTrajectories.equals(_existingTrajectories)) {
          return new RoomOpenHelper.ValidationResult(false, "trajectories(com.pinpoint.app.data.local.entity.TrajectoryEntity).\n"
                  + " Expected:\n" + _infoTrajectories + "\n"
                  + " Found:\n" + _existingTrajectories);
        }
        final HashMap<String, TableInfo.Column> _columnsDeliverySessions = new HashMap<String, TableInfo.Column>(11);
        _columnsDeliverySessions.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsDeliverySessions.put("order_id", new TableInfo.Column("order_id", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsDeliverySessions.put("courier_id", new TableInfo.Column("courier_id", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsDeliverySessions.put("building_external_id", new TableInfo.Column("building_external_id", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsDeliverySessions.put("start_time", new TableInfo.Column("start_time", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsDeliverySessions.put("end_time", new TableInfo.Column("end_time", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsDeliverySessions.put("temperature_model", new TableInfo.Column("temperature_model", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsDeliverySessions.put("start_temperature", new TableInfo.Column("start_temperature", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsDeliverySessions.put("predicted_temperature", new TableInfo.Column("predicted_temperature", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsDeliverySessions.put("predicted_eta", new TableInfo.Column("predicted_eta", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsDeliverySessions.put("transport_mode", new TableInfo.Column("transport_mode", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysDeliverySessions = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesDeliverySessions = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoDeliverySessions = new TableInfo("delivery_sessions", _columnsDeliverySessions, _foreignKeysDeliverySessions, _indicesDeliverySessions);
        final TableInfo _existingDeliverySessions = TableInfo.read(db, "delivery_sessions");
        if (!_infoDeliverySessions.equals(_existingDeliverySessions)) {
          return new RoomOpenHelper.ValidationResult(false, "delivery_sessions(com.pinpoint.app.data.local.entity.DeliverySessionEntity).\n"
                  + " Expected:\n" + _infoDeliverySessions + "\n"
                  + " Found:\n" + _existingDeliverySessions);
        }
        return new RoomOpenHelper.ValidationResult(true, null);
      }
    }, "c337ff5a1f29a73634efb6613f605a2b", "0e648749f6af821f0620d1c8e0840baa");
    final SupportSQLiteOpenHelper.Configuration _sqliteConfig = SupportSQLiteOpenHelper.Configuration.builder(config.context).name(config.name).callback(_openCallback).build();
    final SupportSQLiteOpenHelper _helper = config.sqliteOpenHelperFactory.create(_sqliteConfig);
    return _helper;
  }

  @Override
  @NonNull
  protected InvalidationTracker createInvalidationTracker() {
    final HashMap<String, String> _shadowTablesMap = new HashMap<String, String>(0);
    final HashMap<String, Set<String>> _viewTables = new HashMap<String, Set<String>>(0);
    return new InvalidationTracker(this, _shadowTablesMap, _viewTables, "buildings","entrances","trajectories","delivery_sessions");
  }

  @Override
  public void clearAllTables() {
    super.assertNotMainThread();
    final SupportSQLiteDatabase _db = super.getOpenHelper().getWritableDatabase();
    final boolean _supportsDeferForeignKeys = android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.LOLLIPOP;
    try {
      if (!_supportsDeferForeignKeys) {
        _db.execSQL("PRAGMA foreign_keys = FALSE");
      }
      super.beginTransaction();
      if (_supportsDeferForeignKeys) {
        _db.execSQL("PRAGMA defer_foreign_keys = TRUE");
      }
      _db.execSQL("DELETE FROM `buildings`");
      _db.execSQL("DELETE FROM `entrances`");
      _db.execSQL("DELETE FROM `trajectories`");
      _db.execSQL("DELETE FROM `delivery_sessions`");
      super.setTransactionSuccessful();
    } finally {
      super.endTransaction();
      if (!_supportsDeferForeignKeys) {
        _db.execSQL("PRAGMA foreign_keys = TRUE");
      }
      _db.query("PRAGMA wal_checkpoint(FULL)").close();
      if (!_db.inTransaction()) {
        _db.execSQL("VACUUM");
      }
    }
  }

  @Override
  @NonNull
  protected Map<Class<?>, List<Class<?>>> getRequiredTypeConverters() {
    final HashMap<Class<?>, List<Class<?>>> _typeConvertersMap = new HashMap<Class<?>, List<Class<?>>>();
    _typeConvertersMap.put(BuildingDao.class, BuildingDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(TrajectoryDao.class, TrajectoryDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(DeliverySessionDao.class, DeliverySessionDao_Impl.getRequiredConverters());
    return _typeConvertersMap;
  }

  @Override
  @NonNull
  public Set<Class<? extends AutoMigrationSpec>> getRequiredAutoMigrationSpecs() {
    final HashSet<Class<? extends AutoMigrationSpec>> _autoMigrationSpecsSet = new HashSet<Class<? extends AutoMigrationSpec>>();
    return _autoMigrationSpecsSet;
  }

  @Override
  @NonNull
  public List<Migration> getAutoMigrations(
      @NonNull final Map<Class<? extends AutoMigrationSpec>, AutoMigrationSpec> autoMigrationSpecs) {
    final List<Migration> _autoMigrations = new ArrayList<Migration>();
    return _autoMigrations;
  }

  @Override
  public BuildingDao buildingDao() {
    if (_buildingDao != null) {
      return _buildingDao;
    } else {
      synchronized(this) {
        if(_buildingDao == null) {
          _buildingDao = new BuildingDao_Impl(this);
        }
        return _buildingDao;
      }
    }
  }

  @Override
  public TrajectoryDao trajectoryDao() {
    if (_trajectoryDao != null) {
      return _trajectoryDao;
    } else {
      synchronized(this) {
        if(_trajectoryDao == null) {
          _trajectoryDao = new TrajectoryDao_Impl(this);
        }
        return _trajectoryDao;
      }
    }
  }

  @Override
  public DeliverySessionDao deliverySessionDao() {
    if (_deliverySessionDao != null) {
      return _deliverySessionDao;
    } else {
      synchronized(this) {
        if(_deliverySessionDao == null) {
          _deliverySessionDao = new DeliverySessionDao_Impl(this);
        }
        return _deliverySessionDao;
      }
    }
  }
}
