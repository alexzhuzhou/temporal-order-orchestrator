"""
CLI tool for interacting with the Order Orchestration System
Provides commands to start workflows and send signals
"""

import asyncio
import uuid
import sys
from datetime import timedelta
from temporalio.client import Client

from sqlalchemy import text

from temporal_app.config import TEMPORAL_HOST, ORDER_TASK_QUEUE
from temporal_app.workflows import OrderWorkflow
from temporal_app.db import SessionLocal


async def start_order(
    order_id: str = None,
    payment_id: str = None,
    customer_id: str = None,
    customer_name: str = None,
    order_total: float = 100.0,
    priority: str = "NORMAL",
):
    """Start a new order workflow"""
    client = await Client.connect(TEMPORAL_HOST)

    # Generate IDs if not provided
    if not order_id:
        order_id = f"order-{uuid.uuid4().hex[:8]}"
    if not payment_id:
        payment_id = f"payment-{uuid.uuid4().hex[:8]}"
    if not customer_id:
        customer_id = f"cust-{uuid.uuid4().hex[:8]}"

    # Create customer if not exists (for demo purposes)
    if not customer_name:
        customer_name = f"Customer {customer_id[-4:]}"

    # Check if customer exists, create if not
    with SessionLocal() as db, db.begin():
        existing = db.execute(
            text("SELECT id FROM customers WHERE id = :id"),
            {"id": customer_id}
        ).one_or_none()

        if not existing:
            db.execute(
                text("""
                    INSERT INTO customers (id, name, email)
                    VALUES (:id, :name, :email)
                """),
                {
                    "id": customer_id,
                    "name": customer_name,
                    "email": f"{customer_id}@example.com",
                },
            )
            print(f"✓ Created customer: {customer_id} ({customer_name})")

    print(f"\n🚀 Starting OrderWorkflow")
    print(f"   Order ID: {order_id}")
    print(f"   Payment ID: {payment_id}")
    print(f"   Customer ID: {customer_id}")
    print(f"   Customer Name: {customer_name}")
    print(f"   Order Total: ${order_total:.2f}")
    print(f"   Priority: {priority}")
    print(f"   Task Queue: {ORDER_TASK_QUEUE}")

    handle = await client.start_workflow(
        OrderWorkflow.run,
        args=[order_id, payment_id, customer_id, customer_name, order_total, priority],
        id=order_id,
        task_queue=ORDER_TASK_QUEUE,
        run_timeout=timedelta(seconds=15),
    )

    print(f"\n✓ Workflow started!")
    print(f"   Workflow ID: {handle.id}")
    print(f"   Run ID: {handle.result_run_id}")
    print(f"\n⏳ Workflow is now waiting for manual approval...")
    print(f"\nTo approve this order, run:")
    print(f"   python -m scripts.cli approve {order_id}")
    print(f"\nTo cancel this order, run:")
    print(f"   python -m scripts.cli cancel {order_id}")
    print(f"\nTo check status, run:")
    print(f"   python -m scripts.cli status {order_id}")


async def approve_order(order_id: str):
    """Send approve signal to a workflow"""
    client = await Client.connect(TEMPORAL_HOST)

    print(f"\n✓ Sending approve_order signal to {order_id}...")

    handle = client.get_workflow_handle(order_id)
    await handle.signal(OrderWorkflow.approve_order)

    print(f"✓ Approval signal sent!")
    print(f"   The workflow will now proceed to payment processing.")


async def cancel_order(order_id: str):
    """Send cancel signal to a workflow"""
    client = await Client.connect(TEMPORAL_HOST)

    print(f"\n⚠️  Sending cancel_order signal to {order_id}...")

    handle = client.get_workflow_handle(order_id)
    await handle.signal(OrderWorkflow.cancel_order)

    print(f"✓ Cancellation signal sent!")
    print(f"   The workflow will be cancelled (if not yet paid).")


async def update_address(order_id: str, street: str, city: str, state: str, zip_code: str):
    """Send update address signal to a workflow"""
    client = await Client.connect(TEMPORAL_HOST)

    address = {
        "street": street,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "country": "USA"
    }

    print(f"\n📍 Sending update_address signal to {order_id}...")
    print(f"   New address: {street}, {city}, {state} {zip_code}")

    handle = client.get_workflow_handle(order_id)
    await handle.signal(OrderWorkflow.update_address, address)

    print(f"✓ Address update signal sent!")


async def get_status(order_id: str):
    """Query workflow status"""
    client = await Client.connect(TEMPORAL_HOST)

    print(f"\n🔍 Querying status for {order_id}...")

    handle = client.get_workflow_handle(order_id)

    # Get workflow description
    try:
        description = await handle.describe()
        print(f"\n📊 Workflow Status:")
        print(f"   Status: {description.status.name}")
        print(f"   Run ID: {description.run_id}")
        print(f"   Start Time: {description.start_time}")
    except Exception as e:
        print(f"   Could not get workflow description: {e}")

    # Query custom status
    try:
        status = await handle.query(OrderWorkflow.status)
        print(f"\n📋 Order Details:")
        print(f"   State: {status.get('state')}")
        print(f"   Cancelled: {status.get('cancelled', False)}")
        print(f"   Manual Review Approved: {status.get('manual_review_approved', False)}")
        if status.get('updated_address'):
            print(f"   Updated Address: {status.get('updated_address')}")
        if status.get('last_error'):
            print(f"   Last Error: {status.get('last_error')}")
    except Exception as e:
        print(f"   Could not query workflow status: {e}")


async def wait_for_result(order_id: str):
    """Wait for workflow result"""
    client = await Client.connect(TEMPORAL_HOST)

    print(f"\n⏳ Waiting for workflow {order_id} to complete...")

    handle = client.get_workflow_handle(order_id)

    try:
        result = await handle.result()
        print(f"\n✓ Workflow completed!")
        print(f"   Result: {result}")

        status = await handle.query(OrderWorkflow.status)
        print(f"   Final State: {status.get('state')}")
    except Exception as e:
        print(f"\n❌ Workflow failed or was cancelled")
        print(f"   Error: {e}")


def print_usage():
    """Print usage information"""
    print("\n📦 Order Orchestration CLI")
    print("\nUsage:")
    print("  python -m scripts.cli <command> [arguments]")
    print("\nCommands:")
    print("  start [order_id] [payment_id] [customer_id] [customer_name] [order_total] [priority]")
    print("                                  - Start a new order workflow")
    print("                                    All arguments are optional")
    print("                                    Priority: NORMAL, HIGH, URGENT (default: NORMAL)")
    print("  approve <order_id>              - Approve an order (manual review)")
    print("  cancel <order_id>               - Cancel an order")
    print("  update-address <order_id> <street> <city> <state> <zip>")
    print("                                  - Update shipping address")
    print("  status <order_id>               - Get workflow status")
    print("  wait <order_id>                 - Wait for workflow result")
    print("\nExamples:")
    print("  python -m scripts.cli start")
    print("  python -m scripts.cli start order-001 payment-001 cust-001 \"John Doe\" 250.50 HIGH")
    print("  python -m scripts.cli approve order-abc123")
    print("  python -m scripts.cli cancel order-abc123")
    print("  python -m scripts.cli update-address order-abc123 \"123 Main St\" \"New York\" \"NY\" \"10001\"")
    print("  python -m scripts.cli status order-abc123")
    print()


async def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "start":
            order_id = sys.argv[2] if len(sys.argv) > 2 else None
            payment_id = sys.argv[3] if len(sys.argv) > 3 else None
            customer_id = sys.argv[4] if len(sys.argv) > 4 else None
            customer_name = sys.argv[5] if len(sys.argv) > 5 else None
            order_total = float(sys.argv[6]) if len(sys.argv) > 6 else 100.0
            priority = sys.argv[7] if len(sys.argv) > 7 else "NORMAL"
            await start_order(order_id, payment_id, customer_id, customer_name, order_total, priority)

        elif command == "approve":
            if len(sys.argv) < 3:
                print("❌ Error: order_id required")
                print_usage()
                sys.exit(1)
            await approve_order(sys.argv[2])

        elif command == "cancel":
            if len(sys.argv) < 3:
                print("❌ Error: order_id required")
                print_usage()
                sys.exit(1)
            await cancel_order(sys.argv[2])

        elif command == "update-address":
            if len(sys.argv) < 7:
                print("❌ Error: address components required")
                print_usage()
                sys.exit(1)
            await update_address(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])

        elif command == "status":
            if len(sys.argv) < 3:
                print("❌ Error: order_id required")
                print_usage()
                sys.exit(1)
            await get_status(sys.argv[2])

        elif command == "wait":
            if len(sys.argv) < 3:
                print("❌ Error: order_id required")
                print_usage()
                sys.exit(1)
            await wait_for_result(sys.argv[2])

        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
