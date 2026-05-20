package com.pinpoint.app.data.local.dao;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityDeletionOrUpdateAdapter;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.pinpoint.app.data.local.entity.DeliverySessionEntity;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Long;
import java.lang.Object;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import javax.annotation.processing.Generated;
import kotlin.Unit;
import kotlin.coroutines.Continuation;
import kotlinx.coroutines.flow.Flow;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class DeliverySessionDao_Impl implements DeliverySessionDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<DeliverySessionEntity> __insertionAdapterOfDeliverySessionEntity;

  private final EntityDeletionOrUpdateAdapter<DeliverySessionEntity> __updateAdapterOfDeliverySessionEntity;

  public DeliverySessionDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfDeliverySessionEntity = new EntityInsertionAdapter<DeliverySessionEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `delivery_sessions` (`id`,`order_id`,`courier_id`,`building_external_id`,`start_time`,`end_time`,`temperature_model`,`start_temperature`,`predicted_temperature`,`predicted_eta`,`transport_mode`) VALUES (nullif(?, 0),?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final DeliverySessionEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindString(2, entity.getOrderId());
        statement.bindString(3, entity.getCourierId());
        statement.bindString(4, entity.getBuildingExternalId());
        statement.bindLong(5, entity.getStartTime());
        if (entity.getEndTime() == null) {
          statement.bindNull(6);
        } else {
          statement.bindLong(6, entity.getEndTime());
        }
        statement.bindString(7, entity.getTemperatureModel());
        statement.bindDouble(8, entity.getStartTemperature());
        statement.bindDouble(9, entity.getPredictedTemperature());
        statement.bindLong(10, entity.getPredictedEta());
        if (entity.getTransportMode() == null) {
          statement.bindNull(11);
        } else {
          statement.bindString(11, entity.getTransportMode());
        }
      }
    };
    this.__updateAdapterOfDeliverySessionEntity = new EntityDeletionOrUpdateAdapter<DeliverySessionEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `delivery_sessions` SET `id` = ?,`order_id` = ?,`courier_id` = ?,`building_external_id` = ?,`start_time` = ?,`end_time` = ?,`temperature_model` = ?,`start_temperature` = ?,`predicted_temperature` = ?,`predicted_eta` = ?,`transport_mode` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final DeliverySessionEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindString(2, entity.getOrderId());
        statement.bindString(3, entity.getCourierId());
        statement.bindString(4, entity.getBuildingExternalId());
        statement.bindLong(5, entity.getStartTime());
        if (entity.getEndTime() == null) {
          statement.bindNull(6);
        } else {
          statement.bindLong(6, entity.getEndTime());
        }
        statement.bindString(7, entity.getTemperatureModel());
        statement.bindDouble(8, entity.getStartTemperature());
        statement.bindDouble(9, entity.getPredictedTemperature());
        statement.bindLong(10, entity.getPredictedEta());
        if (entity.getTransportMode() == null) {
          statement.bindNull(11);
        } else {
          statement.bindString(11, entity.getTransportMode());
        }
        statement.bindLong(12, entity.getId());
      }
    };
  }

  @Override
  public Object insertSession(final DeliverySessionEntity session,
      final Continuation<? super Long> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Long>() {
      @Override
      @NonNull
      public Long call() throws Exception {
        __db.beginTransaction();
        try {
          final Long _result = __insertionAdapterOfDeliverySessionEntity.insertAndReturnId(session);
          __db.setTransactionSuccessful();
          return _result;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updateSession(final DeliverySessionEntity session,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfDeliverySessionEntity.handle(session);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object getSessionByOrderId(final String orderId,
      final Continuation<? super DeliverySessionEntity> $completion) {
    final String _sql = "SELECT * FROM delivery_sessions WHERE order_id = ? LIMIT 1";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, orderId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<DeliverySessionEntity>() {
      @Override
      @Nullable
      public DeliverySessionEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfOrderId = CursorUtil.getColumnIndexOrThrow(_cursor, "order_id");
          final int _cursorIndexOfCourierId = CursorUtil.getColumnIndexOrThrow(_cursor, "courier_id");
          final int _cursorIndexOfBuildingExternalId = CursorUtil.getColumnIndexOrThrow(_cursor, "building_external_id");
          final int _cursorIndexOfStartTime = CursorUtil.getColumnIndexOrThrow(_cursor, "start_time");
          final int _cursorIndexOfEndTime = CursorUtil.getColumnIndexOrThrow(_cursor, "end_time");
          final int _cursorIndexOfTemperatureModel = CursorUtil.getColumnIndexOrThrow(_cursor, "temperature_model");
          final int _cursorIndexOfStartTemperature = CursorUtil.getColumnIndexOrThrow(_cursor, "start_temperature");
          final int _cursorIndexOfPredictedTemperature = CursorUtil.getColumnIndexOrThrow(_cursor, "predicted_temperature");
          final int _cursorIndexOfPredictedEta = CursorUtil.getColumnIndexOrThrow(_cursor, "predicted_eta");
          final int _cursorIndexOfTransportMode = CursorUtil.getColumnIndexOrThrow(_cursor, "transport_mode");
          final DeliverySessionEntity _result;
          if (_cursor.moveToFirst()) {
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpOrderId;
            _tmpOrderId = _cursor.getString(_cursorIndexOfOrderId);
            final String _tmpCourierId;
            _tmpCourierId = _cursor.getString(_cursorIndexOfCourierId);
            final String _tmpBuildingExternalId;
            _tmpBuildingExternalId = _cursor.getString(_cursorIndexOfBuildingExternalId);
            final long _tmpStartTime;
            _tmpStartTime = _cursor.getLong(_cursorIndexOfStartTime);
            final Long _tmpEndTime;
            if (_cursor.isNull(_cursorIndexOfEndTime)) {
              _tmpEndTime = null;
            } else {
              _tmpEndTime = _cursor.getLong(_cursorIndexOfEndTime);
            }
            final String _tmpTemperatureModel;
            _tmpTemperatureModel = _cursor.getString(_cursorIndexOfTemperatureModel);
            final double _tmpStartTemperature;
            _tmpStartTemperature = _cursor.getDouble(_cursorIndexOfStartTemperature);
            final double _tmpPredictedTemperature;
            _tmpPredictedTemperature = _cursor.getDouble(_cursorIndexOfPredictedTemperature);
            final long _tmpPredictedEta;
            _tmpPredictedEta = _cursor.getLong(_cursorIndexOfPredictedEta);
            final String _tmpTransportMode;
            if (_cursor.isNull(_cursorIndexOfTransportMode)) {
              _tmpTransportMode = null;
            } else {
              _tmpTransportMode = _cursor.getString(_cursorIndexOfTransportMode);
            }
            _result = new DeliverySessionEntity(_tmpId,_tmpOrderId,_tmpCourierId,_tmpBuildingExternalId,_tmpStartTime,_tmpEndTime,_tmpTemperatureModel,_tmpStartTemperature,_tmpPredictedTemperature,_tmpPredictedEta,_tmpTransportMode);
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
  public Flow<DeliverySessionEntity> observeLatestSession(final String courierId) {
    final String _sql = "SELECT * FROM delivery_sessions WHERE courier_id = ? ORDER BY start_time DESC LIMIT 1";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, courierId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"delivery_sessions"}, new Callable<DeliverySessionEntity>() {
      @Override
      @Nullable
      public DeliverySessionEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfOrderId = CursorUtil.getColumnIndexOrThrow(_cursor, "order_id");
          final int _cursorIndexOfCourierId = CursorUtil.getColumnIndexOrThrow(_cursor, "courier_id");
          final int _cursorIndexOfBuildingExternalId = CursorUtil.getColumnIndexOrThrow(_cursor, "building_external_id");
          final int _cursorIndexOfStartTime = CursorUtil.getColumnIndexOrThrow(_cursor, "start_time");
          final int _cursorIndexOfEndTime = CursorUtil.getColumnIndexOrThrow(_cursor, "end_time");
          final int _cursorIndexOfTemperatureModel = CursorUtil.getColumnIndexOrThrow(_cursor, "temperature_model");
          final int _cursorIndexOfStartTemperature = CursorUtil.getColumnIndexOrThrow(_cursor, "start_temperature");
          final int _cursorIndexOfPredictedTemperature = CursorUtil.getColumnIndexOrThrow(_cursor, "predicted_temperature");
          final int _cursorIndexOfPredictedEta = CursorUtil.getColumnIndexOrThrow(_cursor, "predicted_eta");
          final int _cursorIndexOfTransportMode = CursorUtil.getColumnIndexOrThrow(_cursor, "transport_mode");
          final DeliverySessionEntity _result;
          if (_cursor.moveToFirst()) {
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpOrderId;
            _tmpOrderId = _cursor.getString(_cursorIndexOfOrderId);
            final String _tmpCourierId;
            _tmpCourierId = _cursor.getString(_cursorIndexOfCourierId);
            final String _tmpBuildingExternalId;
            _tmpBuildingExternalId = _cursor.getString(_cursorIndexOfBuildingExternalId);
            final long _tmpStartTime;
            _tmpStartTime = _cursor.getLong(_cursorIndexOfStartTime);
            final Long _tmpEndTime;
            if (_cursor.isNull(_cursorIndexOfEndTime)) {
              _tmpEndTime = null;
            } else {
              _tmpEndTime = _cursor.getLong(_cursorIndexOfEndTime);
            }
            final String _tmpTemperatureModel;
            _tmpTemperatureModel = _cursor.getString(_cursorIndexOfTemperatureModel);
            final double _tmpStartTemperature;
            _tmpStartTemperature = _cursor.getDouble(_cursorIndexOfStartTemperature);
            final double _tmpPredictedTemperature;
            _tmpPredictedTemperature = _cursor.getDouble(_cursorIndexOfPredictedTemperature);
            final long _tmpPredictedEta;
            _tmpPredictedEta = _cursor.getLong(_cursorIndexOfPredictedEta);
            final String _tmpTransportMode;
            if (_cursor.isNull(_cursorIndexOfTransportMode)) {
              _tmpTransportMode = null;
            } else {
              _tmpTransportMode = _cursor.getString(_cursorIndexOfTransportMode);
            }
            _result = new DeliverySessionEntity(_tmpId,_tmpOrderId,_tmpCourierId,_tmpBuildingExternalId,_tmpStartTime,_tmpEndTime,_tmpTemperatureModel,_tmpStartTemperature,_tmpPredictedTemperature,_tmpPredictedEta,_tmpTransportMode);
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

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
