from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from temporalio import workflow

from .activities import (
    receive_order_activity,
    validate_order_activity,
    charge_payment_activity,
    mark_order_shipped_activity,
    prepare_package_activity,
    dispatch_carrier_activity,
)
from .activities import activity_opts


@workflow.defn
class ShippingWorkflow:
    def __init__(self) -> None:
        self.state: str = "INIT"
        self.last_error: Optional[str] = None

    @workflow.run
    async def run(self, order: dict) -> str:
        self.state = "PREPARING_PACKAGE"
        await workflow.execute_activity(
            prepare_package_activity,
            args=[order],
            **activity_opts(),
        )

        self.state = "DISPATCHING"
        await workflow.execute_activity(
            dispatch_carrier_activity,
            args=[order],
            **activity_opts(),
        )

        self.state = "DONE"
        return "DISPATCHED"

    @workflow.query
    def status(self) -> dict:
        return {"state": self.state, "last_error": self.last_error}
    
@workflow.defn
class OrderWorkflow:
    def __init__(self) -> None:
        self.state: str = "INIT"
        self.last_error: Optional[str] = None

    @workflow.query
    def status(self) -> dict:
        return {
            "state": self.state,
            "last_error": self.last_error,
        }

    @workflow.run
    async def run(self, order_id: str, payment_id: str) -> str:
        # Step 1: receive
        self.state = "RECEIVING"
        order = await workflow.execute_activity(
            receive_order_activity,
            args=[order_id],
            **activity_opts(),
        )

        # Step 2: validate
        self.state = "VALIDATING"
        await workflow.execute_activity(
            validate_order_activity,
            args=[order],
            **activity_opts(),
        )

        # Step 3: charge payment
        self.state = "CHARGING_PAYMENT"
        await workflow.execute_activity(
            charge_payment_activity,
            args=[order, payment_id],
            **activity_opts(),
        )

        # Step 4: shipping as child workflow (simple, no cross-signals yet)
        self.state = "SHIPPING"
        shipping_result = await workflow.execute_child_workflow(
            ShippingWorkflow.run,
            args=[order],
        )

        # Step 5: mark order shipped in DB
        self.state = "MARKING_SHIPPED"
        await workflow.execute_activity(
            mark_order_shipped_activity,
            args=[order],
            **activity_opts(),
        )

        self.state = "COMPLETED"
        return shipping_result

