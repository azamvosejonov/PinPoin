package com.pinpoint.app.data.local.dao;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.pinpoint.app.data.local.entity.TrajectoryEntity;
import java.lang.Class;
import java.lang.Exception;
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
public final class TrajectoryDao_Impl implements TrajectoryDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<TrajectoryEntity> __insertionAdapterOfTrajectoryEntity;

  public TrajectoryDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfTrajectoryEntity = new EntityInsertionAdapter<TrajectoryEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `trajectories` (`id`,`building_external_id`,`courier_id`,`delivered_at`,`data_points`) VALUES (nullif(?, 0),?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TrajectoryEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindString(2, entity.getBuildingExternalId());
        statement.bindString(3, entity.getCourierId());
        statement.bindLong(4, entity.getDeliveredAt());
        statement.bindString(5, entity.getDataPoints());
      }
    };
  }

  @Override
  public Object insertTrajectory(final TrajectoryEntity trajectory,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfTrajectoryEntity.insert(trajectory);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object getRecentTrajectories(final String buildingId, final int limit,
      final Continuation<? super List<TrajectoryEntity>> $completion) {
    final String _sql = "SELECT * FROM trajectories WHERE building_external_id = ? ORDER BY delivered_at DESC LIMIT ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 2);
    int _argIndex = 1;
    _statement.bindString(_argIndex, buildingId);
    _argIndex = 2;
    _statement.bindLong(_argIndex, limit);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<TrajectoryEntity>>() {
      @Override
      @NonNull
      public List<TrajectoryEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfBuildingExternalId = CursorUtil.getColumnIndexOrThrow(_cursor, "building_external_id");
          final int _cursorIndexOfCourierId = CursorUtil.getColumnIndexOrThrow(_cursor, "courier_id");
          final int _cursorIndexOfDeliveredAt = CursorUtil.getColumnIndexOrThrow(_cursor, "delivered_at");
          final int _cursorIndexOfDataPoints = CursorUtil.getColumnIndexOrThrow(_cursor, "data_points");
          final List<TrajectoryEntity> _result = new ArrayList<TrajectoryEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final TrajectoryEntity _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpBuildingExternalId;
            _tmpBuildingExternalId = _cursor.getString(_cursorIndexOfBuildingExternalId);
            final String _tmpCourierId;
            _tmpCourierId = _cursor.getString(_cursorIndexOfCourierId);
            final long _tmpDeliveredAt;
            _tmpDeliveredAt = _cursor.getLong(_cursorIndexOfDeliveredAt);
            final String _tmpDataPoints;
            _tmpDataPoints = _cursor.getString(_cursorIndexOfDataPoints);
            _item = new TrajectoryEntity(_tmpId,_tmpBuildingExternalId,_tmpCourierId,_tmpDeliveredAt,_tmpDataPoints);
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

  @Override
  public Flow<List<TrajectoryEntity>> observeTrajectoriesForCourier(final String courierId,
      final int limit) {
    final String _sql = "SELECT * FROM trajectories WHERE courier_id = ? ORDER BY delivered_at DESC LIMIT ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 2);
    int _argIndex = 1;
    _statement.bindString(_argIndex, courierId);
    _argIndex = 2;
    _statement.bindLong(_argIndex, limit);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"trajectories"}, new Callable<List<TrajectoryEntity>>() {
      @Override
      @NonNull
      public List<TrajectoryEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfBuildingExternalId = CursorUtil.getColumnIndexOrThrow(_cursor, "building_external_id");
          final int _cursorIndexOfCourierId = CursorUtil.getColumnIndexOrThrow(_cursor, "courier_id");
          final int _cursorIndexOfDeliveredAt = CursorUtil.getColumnIndexOrThrow(_cursor, "delivered_at");
          final int _cursorIndexOfDataPoints = CursorUtil.getColumnIndexOrThrow(_cursor, "data_points");
          final List<TrajectoryEntity> _result = new ArrayList<TrajectoryEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final TrajectoryEntity _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpBuildingExternalId;
            _tmpBuildingExternalId = _cursor.getString(_cursorIndexOfBuildingExternalId);
            final String _tmpCourierId;
            _tmpCourierId = _cursor.getString(_cursorIndexOfCourierId);
            final long _tmpDeliveredAt;
            _tmpDeliveredAt = _cursor.getLong(_cursorIndexOfDeliveredAt);
            final String _tmpDataPoints;
            _tmpDataPoints = _cursor.getString(_cursorIndexOfDataPoints);
            _item = new TrajectoryEntity(_tmpId,_tmpBuildingExternalId,_tmpCourierId,_tmpDeliveredAt,_tmpDataPoints);
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

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
