import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from temporalio.client import Client
from temporalio.worker import Worker

from temporal_app.config import TEMPORAL_HOST, ORDER_TASK_QUEUE, SHIPPING_TASK_QUEUE
from temporal_app.workflows import OrderWorkflow, ShippingWorkflow
from temporal_app.activities import (
    receive_order_activity,
    validate_order_activity,
    charge_payment_activity,
    mark_order_shipped_activity,
    prepare_package_activity,
    dispatch_carrier_activity,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run two workers: one for order processing, one for shipping."""
    logger.info(f"Connecting to Temporal at {TEMPORAL_HOST}")
    client = await Client.connect(TEMPORAL_HOST)

    # Worker 1: Order Processing (order-tq)
    # Handles OrderWorkflow and order-related activities
    logger.info(f"Creating Order Worker on task queue: {ORDER_TASK_QUEUE}")
    order_worker = Worker(
        client=client,
        task_queue=ORDER_TASK_QUEUE,
        workflows=[OrderWorkflow],
        activities=[
            receive_order_activity,
            validate_order_activity,
            charge_payment_activity,
            mark_order_shipped_activity,
        ],
    )

    # Worker 2: Shipping Processing (shipping-tq)
    # Handles ShippingWorkflow and shipping-related activities
    logger.info(f"Creating Shipping Worker on task queue: {SHIPPING_TASK_QUEUE}")
    shipping_worker = Worker(
        client=client,
        task_queue=SHIPPING_TASK_QUEUE,
        workflows=[ShippingWorkflow],
        activities=[
            prepare_package_activity,
            dispatch_carrier_activity,
        ],
    )

    # Run both workers concurrently
    logger.info("Starting both workers...")
    await asyncio.gather(
        order_worker.run(),
        shipping_worker.run(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Workers shutting down...")
