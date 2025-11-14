from datetime import timedelta
from temporalio import activity

from . import functions


# Shared timeouts for all activities (will trigger flaky_call sleeps)
ACTIVITY_SCHEDULE_TO_CLOSE = timedelta(seconds=4)
ACTIVITY_START_TO_CLOSE = timedelta(seconds=4)


def activity_opts():
    # Helper so we don't repeat kwargs
    return {
        "schedule_to_close_timeout": ACTIVITY_SCHEDULE_TO_CLOSE,
        "start_to_close_timeout": ACTIVITY_START_TO_CLOSE,
    }


@activity.defn
async def receive_order_activity(order_id: str):
    # Thin wrapper around business logic
    return await functions.order_received(order_id)


@activity.defn
async def validate_order_activity(order: dict) -> bool:
    return await functions.order_validated(order)


@activity.defn
async def charge_payment_activity(order: dict, payment_id: str) -> dict:
    return await functions.payment_charged(order, payment_id)


@activity.defn
async def mark_order_shipped_activity(order: dict) -> str:
    return await functions.order_shipped(order)


@activity.defn
async def prepare_package_activity(order: dict) -> str:
    return await functions.package_prepared(order)


@activity.defn
async def dispatch_carrier_activity(order: dict) -> str:
    return await functions.carrier_dispatched(order)
