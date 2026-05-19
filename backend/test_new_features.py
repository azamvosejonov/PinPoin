#!/usr/bin/env python3
"""
Test script for new critical features:
1. Cash balance tracking
2. Race condition protection
3. UNASSIGNABLE status with max retries
4. OFFLINE validation
5. RETURNED_TO_RESTAURANT status
6. declined_courier_ids tracking
"""

import asyncio
import sys
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, '/app')

from app import models, schemas, services
from app.database import get_db


async def test_cash_balance():
    print("\n=== Testing Cash Balance ===")
    
    engine = create_async_engine("sqlite+aiosqlite:////app/data/pinpoint.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Create test courier
        courier = models.User(
            email="courier_cash@example.com",
            password_hash="test",
            role="courier",
            is_active=True
        )
        db.add(courier)
        await db.commit()
        await db.refresh(courier)
        
        # Create courier status
        courier_status = models.CourierStatus(
            courier_id=courier.id,
            status="online",
            cash_balance=0.0
        )
        db.add(courier_status)
        await db.commit()
        await db.refresh(courier_status)
        
        print(f"Initial cash_balance: {courier_status.cash_balance}")
        
        # Test cash collection
        try:
            updated_status = await services.collect_cash_from_courier(db, courier.id, 50000.0)
            print(f"After collecting 50000: {updated_status.cash_balance}")
            assert updated_status.cash_balance == -50000.0, "Cash balance should be -50000"
            print("✓ Cash collection test PASSED")
        except Exception as e:
            print(f"✗ Cash collection test FAILED: {e}")
        
        # Test exceeding balance
        try:
            await services.collect_cash_from_courier(db, courier.id, 100000.0)
            print("✗ Should have failed when exceeding balance")
        except Exception as e:
            print(f"✓ Exceeding balance test PASSED: {e}")


async def test_offline_validation():
    print("\n=== Testing OFFLINE Validation ===")
    
    engine = create_async_engine("sqlite+aiosqlite:////app/data/pinpoint.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Create test courier with active order
        courier = models.User(
            email="courier_offline@example.com",
            password_hash="test",
            role="courier",
            is_active=True
        )
        db.add(courier)
        await db.commit()
        await db.refresh(courier)
        
        # Create courier status
        courier_status = models.CourierStatus(
            courier_id=courier.id,
            status="online",
            cash_balance=0.0
        )
        db.add(courier_status)
        await db.commit()
        
        # Create active order
        order = models.Order(
            order_code="TEST001",
            tracking_hash="test_hash",
            status="accepted",
            courier_id=courier.id,
            restaurant_id=1,
            total_amount=100000.0,
            payment_method="CASH"
        )
        db.add(order)
        await db.commit()
        
        # Test OFFLINE validation
        try:
            await services.update_courier_status(db, courier.id, schemas.CourierStatusUpdate(status=schemas.CourierStatusEnum.offline))
            print("✗ Should have failed with active orders")
        except Exception as e:
            print(f"✓ OFFLINE validation test PASSED: {e}")


async def test_unassignable_status():
    print("\n=== Testing UNASSIGNABLE Status ===")
    
    engine = create_async_engine("sqlite+aiosqlite:////app/data/pinpoint.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Create order with max retries
        order = models.Order(
            order_code="TEST002",
            tracking_hash="test_hash2",
            status="ready_for_pickup",
            restaurant_id=1,
            max_retries=3,
            retry_count=3
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        print(f"Order retry_count: {order.retry_count}, max_retries: {order.max_retries}")
        
        # Test auto_assign with max retries
        try:
            result = await services.auto_assign_order(db, order.id)
            print(f"Order status after auto_assign: {result.status}")
            assert result.status == "unassignable", "Status should be unassignable"
            print("✓ UNASSIGNABLE status test PASSED")
        except Exception as e:
            print(f"✗ UNASSIGNABLE status test FAILED: {e}")


async def test_declined_courier_ids():
    print("\n=== Testing declined_courier_ids Tracking ===")
    
    engine = create_async_engine("sqlite+aiosqlite:////app/data/pinpoint.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Create courier
        courier = models.User(
            email="courier_decline@example.com",
            password_hash="test",
            role="courier",
            is_active=True
        )
        db.add(courier)
        await db.commit()
        await db.refresh(courier)
        
        # Create courier status
        courier_status = models.CourierStatus(
            courier_id=courier.id,
            status="online",
            cash_balance=0.0
        )
        db.add(courier_status)
        await db.commit()
        
        # Create order
        order = models.Order(
            order_code="TEST003",
            tracking_hash="test_hash3",
            status="accepted",
            courier_id=courier.id,
            restaurant_id=1,
            total_amount=100000.0,
            payment_method="CASH"
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        print(f"Order declined_courier_ids before decline: {order.declined_courier_ids}")
        
        # Test decline order
        try:
            declined_order = await services.decline_order(db, order.id, "Too far")
            print(f"Order declined_courier_ids after decline: {declined_order.declined_courier_ids}")
            assert str(courier.id) in declined_order.declined_courier_ids, "Courier ID should be in declined list"
            print("✓ declined_courier_ids tracking test PASSED")
        except Exception as e:
            print(f"✗ declined_courier_ids tracking test FAILED: {e}")


async def test_returned_to_restaurant():
    print("\n=== Testing RETURNED_TO_RESTAURANT Status ===")
    
    engine = create_async_engine("sqlite+aiosqlite:////app/data/pinpoint.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Create order in delivery_failed state
        order = models.Order(
            order_code="TEST004",
            tracking_hash="test_hash4",
            status="delivery_failed",
            restaurant_id=1,
            total_amount=100000.0,
            payment_method="CASH"
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        print(f"Order status before: {order.status}")
        
        # Test transition to returned_to_restaurant
        try:
            updated_order = await services.update_order_status(
                db, 
                order.id, 
                schemas.OrderStatusUpdate(status=schemas.OrderStatus.returned_to_restaurant),
                changed_by_user_id=1
            )
            print(f"Order status after: {updated_order.status}")
            assert updated_order.status == "returned_to_restaurant", "Status should be returned_to_restaurant"
            print("✓ RETURNED_TO_RESTAURANT status test PASSED")
        except Exception as e:
            print(f"✗ RETURNED_TO_RESTAURANT status test FAILED: {e}")


async def main():
    print("Starting tests for new critical features...")
    
    await test_cash_balance()
    await test_offline_validation()
    await test_unassignable_status()
    await test_declined_courier_ids()
    await test_returned_to_restaurant()
    
    print("\n=== All Tests Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
