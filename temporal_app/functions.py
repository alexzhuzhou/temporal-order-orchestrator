import asyncio
import json
import random
from typing import Dict, Any

from sqlalchemy import text

from .db import SessionLocal


async def flaky_call() -> None:
    """Either raise an error or sleep long enough to trigger an activity timeout."""
    rand_num = random.random()
    if rand_num < 0.33:
        raise RuntimeError("Forced failure for testing")
    if rand_num < 0.67:
        await asyncio.sleep(300)  # activity timeouts should fire before this
    # else: succeed immediately


async def order_received(order_id: str) -> Dict[str, Any]:
    await flaky_call()

    # DB write: insert order row + event
    with SessionLocal() as db, db.begin():
        db.execute(
            text("""
                INSERT INTO orders (id, state)
                VALUES (:id, :state)
                ON CONFLICT (id) DO NOTHING
            """),
            {"id": order_id, "state": "RECEIVED"},
        )
        db.execute(
            text("""
                INSERT INTO events (order_id, type, payload_json)
                VALUES (:order_id, :type, :payload)
            """),
            {
                "order_id": order_id,
                "type": "ORDER_RECEIVED",
                "payload": json.dumps({"order_id": order_id}),
            },
        )

    # Return a simple in-memory representation the workflow can carry along
    return {"order_id": order_id, "items": [{"sku": "ABC", "qty": 1}]}


async def order_validated(order: Dict[str, Any]) -> bool:
    await flaky_call()

    if not order.get("items"):
        raise ValueError("No items to validate")

    order_id = order["order_id"]

    with SessionLocal() as db, db.begin():
        db.execute(
            text("UPDATE orders SET state = :state WHERE id = :id"),
            {"state": "VALIDATED", "id": order_id},
        )
        db.execute(
            text("""
                INSERT INTO events (order_id, type, payload_json)
                VALUES (:order_id, :type, :payload)
            """),
            {
                "order_id": order_id,
                "type": "ORDER_VALIDATED",
                "payload": json.dumps(order),
            },
        )

    return True


async def payment_charged(order: Dict[str, Any], payment_id: str) -> Dict[str, Any]:
    """
    Charge payment with idempotency based on payment_id.
    This will be called from an activity with retries – idempotency is critical.
    """
    await flaky_call()

    order_id = order["order_id"]
    amount = sum(i.get("qty", 1) for i in order.get("items", []))

    with SessionLocal() as db, db.begin():
        # Check if we already processed this payment_id
        row = db.execute(
            text("SELECT status, amount FROM payments WHERE payment_id = :pid"),
            {"pid": payment_id},
        ).one_or_none()

        if row:
            # Idempotent: just return existing status
            return {"status": row.status, "amount": row.amount}

        # First time seeing this payment_id: insert as CHARGED
        db.execute(
            text("""
                INSERT INTO payments (payment_id, order_id, status, amount)
                VALUES (:pid, :oid, :status, :amount)
            """),
            {
                "pid": payment_id,
                "oid": order_id,
                "status": "CHARGED",
                "amount": amount,
            },
        )
        db.execute(
            text("""
                UPDATE orders SET state = :state WHERE id = :id
            """),
            {"state": "PAID", "id": order_id},
        )
        db.execute(
            text("""
                INSERT INTO events (order_id, type, payload_json)
                VALUES (:order_id, :type, :payload)
            """),
            {
                "order_id": order_id,
                "type": "PAYMENT_CHARGED",
                "payload": json.dumps(
                    {"payment_id": payment_id, "amount": amount}
                ),
            },
        )

    return {"status": "CHARGED", "amount": amount}


async def order_shipped(order: Dict[str, Any]) -> str:
    await flaky_call()

    order_id = order["order_id"]
    with SessionLocal() as db, db.begin():
        db.execute(
            text("UPDATE orders SET state = :state WHERE id = :id"),
            {"state": "SHIPPED", "id": order_id},
        )
        db.execute(
            text("""
                INSERT INTO events (order_id, type, payload_json)
                VALUES (:order_id, :type, :payload)
            """),
            {
                "order_id": order_id,
                "type": "ORDER_SHIPPED",
                "payload": json.dumps(order),
            },
        )

    return "Shipped"


async def package_prepared(order: Dict[str, Any]) -> str:
    await flaky_call()

    order_id = order["order_id"]
    with SessionLocal() as db, db.begin():
        db.execute(
            text("UPDATE orders SET state = :state WHERE id = :id"),
            {"state": "PACKAGE_PREPARED", "id": order_id},
        )
        db.execute(
            text("""
                INSERT INTO events (order_id, type, payload_json)
                VALUES (:order_id, :type, :payload)
            """),
            {
                "order_id": order_id,
                "type": "PACKAGE_PREPARED",
                "payload": json.dumps(order),
            },
        )

    return "Package ready"


async def carrier_dispatched(order: Dict[str, Any]) -> str:
    await flaky_call()

    order_id = order["order_id"]
    with SessionLocal() as db, db.begin():
        db.execute(
            text("UPDATE orders SET state = :state WHERE id = :id"),
            {"state": "CARRIER_DISPATCHED", "id": order_id},
        )
        db.execute(
            text("""
                INSERT INTO events (order_id, type, payload_json)
                VALUES (:order_id, :type, :payload)
            """),
            {
                "order_id": order_id,
                "type": "CARRIER_DISPATCHED",
                "payload": json.dumps(order),
            },
        )

    return "Dispatched"
