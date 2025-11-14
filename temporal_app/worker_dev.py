import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from .config import TEMPORAL_HOST
from .workflows import OrderWorkflow, ShippingWorkflow
from .activities import (
    receive_order_activity,
    validate_order_activity,
    charge_payment_activity,
    mark_order_shipped_activity,
    prepare_package_activity,
    dispatch_carrier_activity,
)


TASK_QUEUE = "dev-tq"


async def main():
    client = await Client.connect(TEMPORAL_HOST)

    worker = Worker(
        client=client,
        task_queue=TASK_QUEUE,
        workflows=[OrderWorkflow, ShippingWorkflow],
        activities=[
            receive_order_activity,
            validate_order_activity,
            charge_payment_activity,
            mark_order_shipped_activity,
            prepare_package_activity,
            dispatch_carrier_activity,
        ],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
