import asyncio
import uuid
from datetime import timedelta
from temporalio.client import Client

from temporal_app.config import TEMPORAL_HOST, ORDER_TASK_QUEUE
from temporal_app.workflows import OrderWorkflow


async def main():
    client = await Client.connect(TEMPORAL_HOST)

    # Generate unique IDs for each run
    order_id = f"order-{uuid.uuid4().hex[:8]}"
    payment_id = f"payment-{uuid.uuid4().hex[:8]}"

    print(f"Starting OrderWorkflow for order_id={order_id}, payment_id={payment_id}")

    handle = await client.start_workflow(
        OrderWorkflow.run,
        args=[order_id, payment_id],
        id=order_id,
        task_queue=ORDER_TASK_QUEUE,
        run_timeout=timedelta(seconds=15),
    )

    print(f"Started workflow: {handle.id}, run_id={handle.result_run_id}")
    print(f"Workflow is running on task queue: {ORDER_TASK_QUEUE}")
    print("\nWaiting for manual approval... Send approve_order signal to continue")
    print(f"To approve: Use the API or Temporal UI to send 'approve_order' signal to workflow '{order_id}'")

    result = await handle.result()
    print(f"\n✓ Workflow result: {result}")

    status = await handle.query(OrderWorkflow.status)
    print(f"✓ Final status: {status}")


if __name__ == "__main__":
    asyncio.run(main())