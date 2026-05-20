package com.pinpoint.app.data.local.dao;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomDatabaseKt;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.pinpoint.app.data.local.entity.BuildingEntity;
import com.pinpoint.app.data.local.entity.EntranceEntity;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Long;
import java.lang.Object;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import javax.annotation.processing.Generated;
import kotlin.Unit;
import kotlin.coroutines.Continuation;
import kotlinx.coroutines.flow.Flow;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class BuildingDao_Impl implements BuildingDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<BuildingEntity> __insertionAdapterOfBuildingEntity;

  private final EntityInsertionAdapter<EntranceEntity> __insertionAdapterOfEntranceEntity;

  private final SharedSQLiteStatement __preparedStmtOfMarkDomofonFailure;

  private final SharedSQLiteStatement __preparedStmtOfUpdateDomofonCode;

  public BuildingDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfBuildingEntity = new EntityInsertionAdapter<BuildingEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `buildings` (`id`,`building_external_id`,`address`,`latitude`,`longitude`,`building_type`,`difficulty_index`,`has_lift`,`requires_chip`,`entrance_hint`,`updated_at`) VALUES (nullif(?, 0),?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final BuildingEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindString(2, entity.getBuildingExternalId());
        statement.bindString(3, entity.getAddress());
        statement.bindDouble(4, entity.getLatitude());
        statement.bindDouble(5, entity.getLongitude());
        statement.bindString(6, entity.getBuildingType());
        statement.bindLong(7, entity.getDifficultyIndex());
        final int _tmp = entity.getHasLift() ? 1 : 0;
        statement.bindLong(8, _tmp);
        final int _tmp_1 = entity.getRequiresChip() ? 1 : 0;
        statement.bindLong(9, _tmp_1);
        if (entity.getEntranceHint() == null) {
          statement.bindNull(10);
        } else {
          statement.bindString(10, entity.getEntranceHint());
        }
        statement.bindLong(11, entity.getUpdatedAt());
      }
    };
    this.__insertionAdapterOfEntranceEntity = new EntityInsertionAdapter<EntranceEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `entrances` (`id`,`building_id`,`label`,`latitude`,`longitude`,`domofon_code`,`has_barrier`,`validated_count`,`last_validated_at`) VALUES (nullif(?, 0),?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final EntranceEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindLong(2, entity.getBuildingId());
        statement.bindString(3, entity.getLabel());
        statement.bindDouble(4, entity.getLatitude());
        statement.bindDouble(5, entity.getLongitude());
        if (entity.getDomofonCode() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getDomofonCode());
        }
        final int _tmp = entity.getHasBarrier() ? 1 : 0;
        statement.bindLong(7, _tmp);
        statement.bindLong(8, entity.getValidatedCount());
        statement.bindLong(9, entity.getLastValidatedAt());
      }
    };
    this.__preparedStmtOfMarkDomofonFailure = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "UPDATE entrances SET validated_count = CASE WHEN validated_count > 0 THEN validated_count - 1 ELSE 0 END WHERE id = ?";
        return _query;
      }
    };
    this.__preparedStmtOfUpdateDomofonCode = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "UPDATE entrances SET domofon_code = ?, validated_count = validated_count + 1, last_validated_at = ? WHERE id = ?";
        return _query;
      }
    };
  }

  @Override
  public Object upsertBuilding(final BuildingEntity buildingEntity,
      final Continuation<? super Long> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Long>() {
      @Override
      @NonNull
      public Long call() throws Exception {
        __db.beginTransaction();
        try {
          final Long _result = __insertionAdapterOfBuildingEntity.insertAndReturnId(buildingEntity);
          __db.setTransactionSuccessful();
          return _result;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object upsertEntrances(final List<EntranceEntity> entrances,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfEntranceEntity.insert(entrances);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object upsertBuildingWithEntrances(final BuildingEntity building,
      final List<EntranceEntity> entrances, final Continuation<? super Unit> $completion) {
    return RoomDatabaseKt.withTransaction(__db, (__cont) -> BuildingDao.DefaultImpls.upsertBuildingWithEntrances(BuildingDao_Impl.this, building, entrances, __cont), $completion);
  }

  @Override
  public Object markDomofonFailure(final long entranceId,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfMarkDomofonFailure.acquire();
        int _argIndex = 1;
        _stmt.bindLong(_argIndex, entranceId);
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfMarkDomofonFailure.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Object updateDomofonCode(final long entranceId, final String code, final long timestamp,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfUpdateDomofonCode.acquire();
        int _argIndex = 1;
        _stmt.bindString(_argIndex, code);
        _argIndex = 2;
        _stmt.bindLong(_argIndex, timestamp);
        _argIndex = 3;
        _stmt.bindLong(_argIndex, entranceId);
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfUpdateDomofonCode.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<BuildingEntity> observeBuildingByExternalId(final String externalId) {
    final String _sql = "SELECT * FROM buildings WHERE building_external_id = ? LIMIT 1";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, externalId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"buildings"}, new Callable<BuildingEntity>() {
      @Override
      @Nullable
      public BuildingEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfBuildingExternalId = CursorUtil.getColumnIndexOrThrow(_cursor, "building_external_id");
          final int _cursorIndexOfAddress = CursorUtil.getColumnIndexOrThrow(_cursor, "address");
          final int _cursorIndexOfLatitude = CursorUtil.getColumnIndexOrThrow(_cursor, "latitude");
          final int _cursorIndexOfLongitude = CursorUtil.getColumnIndexOrThrow(_cursor, "longitude");
          final int _cursorIndexOfBuildingType = CursorUtil.getColumnIndexOrThrow(_cursor, "building_type");
          final int _cursorIndexOfDifficultyIndex = CursorUtil.getColumnIndexOrThrow(_cursor, "difficulty_index");
          final int _cursorIndexOfHasLift = CursorUtil.getColumnIndexOrThrow(_cursor, "has_lift");
          final int _cursorIndexOfRequiresChip = CursorUtil.getColumnIndexOrThrow(_cursor, "requires_chip");
          final int _cursorIndexOfEntranceHint = CursorUtil.getColumnIndexOrThrow(_cursor, "entrance_hint");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updated_at");
          final BuildingEntity _result;
          if (_cursor.moveToFirst()) {
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpBuildingExternalId;
            _tmpBuildingExternalId = _cursor.getString(_cursorIndexOfBuildingExternalId);
            final String _tmpAddress;
            _tmpAddress = _cursor.getString(_cursorIndexOfAddress);
            final double _tmpLatitude;
            _tmpLatitude = _cursor.getDouble(_cursorIndexOfLatitude);
            final double _tmpLongitude;
            _tmpLongitude = _cursor.getDouble(_cursorIndexOfLongitude);
            final String _tmpBuildingType;
            _tmpBuildingType = _cursor.getString(_cursorIndexOfBuildingType);
            final int _tmpDifficultyIndex;
            _tmpDifficultyIndex = _cursor.getInt(_cursorIndexOfDifficultyIndex);
            final boolean _tmpHasLift;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfHasLift);
            _tmpHasLift = _tmp != 0;
            final boolean _tmpRequiresChip;
            final int _tmp_1;
            _tmp_1 = _cursor.getInt(_cursorIndexOfRequiresChip);
            _tmpRequiresChip = _tmp_1 != 0;
            final String _tmpEntranceHint;
            if (_cursor.isNull(_cursorIndexOfEntranceHint)) {
              _tmpEntranceHint = null;
            } else {
              _tmpEntranceHint = _cursor.getString(_cursorIndexOfEntranceHint);
            }
            final long _tmpUpdatedAt;
            _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            _result = new BuildingEntity(_tmpId,_tmpBuildingExternalId,_tmpAddress,_tmpLatitude,_tmpLongitude,_tmpBuildingType,_tmpDifficultyIndex,_tmpHasLift,_tmpRequiresChip,_tmpEntranceHint,_tmpUpdatedAt);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Object getBuildingByExternalId(final String externalId,
      final Continuation<? super BuildingEntity> $completion) {
    final String _sql = "SELECT * FROM buildings WHERE building_external_id = ? LIMIT 1";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, externalId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<BuildingEntity>() {
      @Override
      @Nullable
      public BuildingEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfBuildingExternalId = CursorUtil.getColumnIndexOrThrow(_cursor, "building_external_id");
          final int _cursorIndexOfAddress = CursorUtil.getColumnIndexOrThrow(_cursor, "address");
          final int _cursorIndexOfLatitude = CursorUtil.getColumnIndexOrThrow(_cursor, "latitude");
          final int _cursorIndexOfLongitude = CursorUtil.getColumnIndexOrThrow(_cursor, "longitude");
          final int _cursorIndexOfBuildingType = CursorUtil.getColumnIndexOrThrow(_cursor, "building_type");
          final int _cursorIndexOfDifficultyIndex = CursorUtil.getColumnIndexOrThrow(_cursor, "difficulty_index");
          final int _cursorIndexOfHasLift = CursorUtil.getColumnIndexOrThrow(_cursor, "has_lift");
          final int _cursorIndexOfRequiresChip = CursorUtil.getColumnIndexOrThrow(_cursor, "requires_chip");
          final int _cursorIndexOfEntranceHint = CursorUtil.getColumnIndexOrThrow(_cursor, "entrance_hint");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updated_at");
          final BuildingEntity _result;
          if (_cursor.moveToFirst()) {
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpBuildingExternalId;
            _tmpBuildingExternalId = _cursor.getString(_cursorIndexOfBuildingExternalId);
            final String _tmpAddress;
            _tmpAddress = _cursor.getString(_cursorIndexOfAddress);
            final double _tmpLatitude;
            _tmpLatitude = _cursor.getDouble(_cursorIndexOfLatitude);
            final double _tmpLongitude;
            _tmpLongitude = _cursor.getDouble(_cursorIndexOfLongitude);
            final String _tmpBuildingType;
            _tmpBuildingType = _cursor.getString(_cursorIndexOfBuildingType);
            final int _tmpDifficultyIndex;
            _tmpDifficultyIndex = _cursor.getInt(_cursorIndexOfDifficultyIndex);
            final boolean _tmpHasLift;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfHasLift);
            _tmpHasLift = _tmp != 0;
            final boolean _tmpRequiresChip;
            final int _tmp_1;
            _tmp_1 = _cursor.getInt(_cursorIndexOfRequiresChip);
            _tmpRequiresChip = _tmp_1 != 0;
            final String _tmpEntranceHint;
            if (_cursor.isNull(_cursorIndexOfEntranceHint)) {
              _tmpEntranceHint = null;
            } else {
              _tmpEntranceHint = _cursor.getString(_cursorIndexOfEntranceHint);
            }
            final long _tmpUpdatedAt;
            _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            _result = new BuildingEntity(_tmpId,_tmpBuildingExternalId,_tmpAddress,_tmpLatitude,_tmpLongitude,_tmpBuildingType,_tmpDifficultyIndex,_tmpHasLift,_tmpRequiresChip,_tmpEntranceHint,_tmpUpdatedAt);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<EntranceEntity>> observeEntrancesByBuilding(final long buildingId) {
    final String _sql = "SELECT * FROM entrances WHERE building_id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, buildingId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"entrances"}, new Callable<List<EntranceEntity>>() {
      @Override
      @NonNull
      public List<EntranceEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfBuildingId = CursorUtil.getColumnIndexOrThrow(_cursor, "building_id");
          final int _cursorIndexOfLabel = CursorUtil.getColumnIndexOrThrow(_cursor, "label");
          final int _cursorIndexOfLatitude = CursorUtil.getColumnIndexOrThrow(_cursor, "latitude");
          final int _cursorIndexOfLongitude = CursorUtil.getColumnIndexOrThrow(_cursor, "longitude");
          final int _cursorIndexOfDomofonCode = CursorUtil.getColumnIndexOrThrow(_cursor, "domofon_code");
          final int _cursorIndexOfHasBarrier = CursorUtil.getColumnIndexOrThrow(_cursor, "has_barrier");
          final int _cursorIndexOfValidatedCount = CursorUtil.getColumnIndexOrThrow(_cursor, "validated_count");
          final int _cursorIndexOfLastValidatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "last_validated_at");
          final List<EntranceEntity> _result = new ArrayList<EntranceEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final EntranceEntity _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final long _tmpBuildingId;
            _tmpBuildingId = _cursor.getLong(_cursorIndexOfBuildingId);
            final String _tmpLabel;
            _tmpLabel = _cursor.getString(_cursorIndexOfLabel);
            final double _tmpLatitude;
            _tmpLatitude = _cursor.getDouble(_cursorIndexOfLatitude);
            final double _tmpLongitude;
            _tmpLongitude = _cursor.getDouble(_cursorIndexOfLongitude);
            final String _tmpDomofonCode;
            if (_cursor.isNull(_cursorIndexOfDomofonCode)) {
              _tmpDomofonCode = null;
            } else {
              _tmpDomofonCode = _cursor.getString(_cursorIndexOfDomofonCode);
            }
            final boolean _tmpHasBarrier;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfHasBarrier);
            _tmpHasBarrier = _tmp != 0;
            final int _tmpValidatedCount;
            _tmpValidatedCount = _cursor.getInt(_cursorIndexOfValidatedCount);
            final long _tmpLastValidatedAt;
            _tmpLastValidatedAt = _cursor.getLong(_cursorIndexOfLastValidatedAt);
            _item = new EntranceEntity(_tmpId,_tmpBuildingId,_tmpLabel,_tmpLatitude,_tmpLongitude,_tmpDomofonCode,_tmpHasBarrier,_tmpValidatedCount,_tmpLastValidatedAt);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Object getEntranceById(final long entranceId,
      final Continuation<? super EntranceEntity> $completion) {
    final String _sql = "SELECT * FROM entrances WHERE id = ? LIMIT 1";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, entranceId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<EntranceEntity>() {
      @Override
      @Nullable
      public EntranceEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfBuildingId = CursorUtil.getColumnIndexOrThrow(_cursor, "building_id");
          final int _cursorIndexOfLabel = CursorUtil.getColumnIndexOrThrow(_cursor, "label");
          final int _cursorIndexOfLatitude = CursorUtil.getColumnIndexOrThrow(_cursor, "latitude");
          final int _cursorIndexOfLongitude = CursorUtil.getColumnIndexOrThrow(_cursor, "longitude");
          final int _cursorIndexOfDomofonCode = CursorUtil.getColumnIndexOrThrow(_cursor, "domofon_code");
          final int _cursorIndexOfHasBarrier = CursorUtil.getColumnIndexOrThrow(_cursor, "has_barrier");
          final int _cursorIndexOfValidatedCount = CursorUtil.getColumnIndexOrThrow(_cursor, "validated_count");
          final int _cursorIndexOfLastValidatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "last_validated_at");
          final EntranceEntity _result;
          if (_cursor.moveToFirst()) {
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final long _tmpBuildingId;
            _tmpBuildingId = _cursor.getLong(_cursorIndexOfBuildingId);
            final String _tmpLabel;
            _tmpLabel = _cursor.getString(_cursorIndexOfLabel);
            final double _tmpLatitude;
            _tmpLatitude = _cursor.getDouble(_cursorIndexOfLatitude);
            final double _tmpLongitude;
            _tmpLongitude = _cursor.getDouble(_cursorIndexOfLongitude);
            final String _tmpDomofonCode;
            if (_cursor.isNull(_cursorIndexOfDomofonCode)) {
              _tmpDomofonCode = null;
            } else {
              _tmpDomofonCode = _cursor.getString(_cursorIndexOfDomofonCode);
            }
            final boolean _tmpHasBarrier;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfHasBarrier);
            _tmpHasBarrier = _tmp != 0;
            final int _tmpValidatedCount;
            _tmpValidatedCount = _cursor.getInt(_cursorIndexOfValidatedCount);
            final long _tmpLastValidatedAt;
            _tmpLastValidatedAt = _cursor.getLong(_cursorIndexOfLastValidatedAt);
            _result = new EntranceEntity(_tmpId,_tmpBuildingId,_tmpLabel,_tmpLatitude,_tmpLongitude,_tmpDomofonCode,_tmpHasBarrier,_tmpValidatedCount,_tmpLastValidatedAt);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object getEntrancesForBuilding(final long buildingId,
      final Continuation<? super List<EntranceEntity>> $completion) {
    final String _sql = "SELECT * FROM entrances WHERE building_id = ? ORDER BY validated_count DESC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, buildingId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<EntranceEntity>>() {
      @Override
      @NonNull
      public List<EntranceEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfBuildingId = CursorUtil.getColumnIndexOrThrow(_cursor, "building_id");
          final int _cursorIndexOfLabel = CursorUtil.getColumnIndexOrThrow(_cursor, "label");
          final int _cursorIndexOfLatitude = CursorUtil.getColumnIndexOrThrow(_cursor, "latitude");
          final int _cursorIndexOfLongitude = CursorUtil.getColumnIndexOrThrow(_cursor, "longitude");
          final int _cursorIndexOfDomofonCode = CursorUtil.getColumnIndexOrThrow(_cursor, "domofon_code");
          final int _cursorIndexOfHasBarrier = CursorUtil.getColumnIndexOrThrow(_cursor, "has_barrier");
          final int _cursorIndexOfValidatedCount = CursorUtil.getColumnIndexOrThrow(_cursor, "validated_count");
          final int _cursorIndexOfLastValidatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "last_validated_at");
          final List<EntranceEntity> _result = new ArrayList<EntranceEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final EntranceEntity _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final long _tmpBuildingId;
            _tmpBuildingId = _cursor.getLong(_cursorIndexOfBuildingId);
            final String _tmpLabel;
            _tmpLabel = _cursor.getString(_cursorIndexOfLabel);
            final double _tmpLatitude;
            _tmpLatitude = _cursor.getDouble(_cursorIndexOfLatitude);
            final double _tmpLongitude;
            _tmpLongitude = _cursor.getDouble(_cursorIndexOfLongitude);
            final String _tmpDomofonCode;
            if (_cursor.isNull(_cursorIndexOfDomofonCode)) {
              _tmpDomofonCode = null;
            } else {
              _tmpDomofonCode = _cursor.getString(_cursorIndexOfDomofonCode);
            }
            final boolean _tmpHasBarrier;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfHasBarrier);
            _tmpHasBarrier = _tmp != 0;
            final int _tmpValidatedCount;
            _tmpValidatedCount = _cursor.getInt(_cursorIndexOfValidatedCount);
            final long _tmpLastValidatedAt;
            _tmpLastValidatedAt = _cursor.getLong(_cursorIndexOfLastValidatedAt);
            _item = new EntranceEntity(_tmpId,_tmpBuildingId,_tmpLabel,_tmpLatitude,_tmpLongitude,_tmpDomofonCode,_tmpHasBarrier,_tmpValidatedCount,_tmpLastValidatedAt);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
