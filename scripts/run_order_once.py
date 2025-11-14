import asyncio
import uuid
from datetime import timedelta
from temporalio.client import Client

from temporal_app.config import TEMPORAL_HOST
from temporal_app.workflows import OrderWorkflow
from temporal_app.worker_dev import TASK_QUEUE


async def main():
    client = await Client.connect(TEMPORAL_HOST)

    # Generate unique IDs for each run
    order_id = f"order-{uuid.uuid4().hex[:8]}"
    payment_id = f"payment-{uuid.uuid4().hex[:8]}"

    handle = await client.start_workflow(
        OrderWorkflow.run,
        args=[order_id, payment_id],
        id=order_id,
        task_queue=TASK_QUEUE,
        run_timeout=timedelta(seconds=15),
    )

    print("Started workflow:", handle.id, handle.result_run_id)

    result = await handle.result()
    print("Workflow result:", result)

    status = await handle.query(OrderWorkflow.status)
    print("Final status:", status)


if __name__ == "__main__":
    asyncio.run(main())