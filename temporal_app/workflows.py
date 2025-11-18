from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import timedelta
import logging

from temporalio import workflow
from temporalio.exceptions import ActivityError, ChildWorkflowError
from temporalio.common import SearchAttributeKey

from .activities import (
    receive_order_activity,
    validate_order_activity,
    charge_payment_activity,
    mark_order_shipped_activity,
    prepare_package_activity,
    dispatch_carrier_activity,
)
from .activities import activity_opts

# Setup logger
logger = logging.getLogger(__name__)

# Define search attribute keys
CUSTOMER_ID_ATTR = SearchAttributeKey.for_keyword("CustomerId")
CUSTOMER_NAME_ATTR = SearchAttributeKey.for_text("CustomerName")
ORDER_TOTAL_ATTR = SearchAttributeKey.for_float("OrderTotal")
PRIORITY_ATTR = SearchAttributeKey.for_keyword("Priority")


@workflow.defn
class ShippingWorkflow:
    def __init__(self) -> None:
        self.state: str = "INIT"
        self.last_error: Optional[str] = None

    @workflow.run
    async def run(self, order: dict) -> str:
        try:
            self.state = "PREPARING_PACKAGE"
            workflow.logger.info(f"ShippingWorkflow: Preparing package for order {order.get('order_id')}")
            await workflow.execute_activity(
                prepare_package_activity,
                args=[order],
                **activity_opts(),
            )

            self.state = "DISPATCHING"
            workflow.logger.info(f"ShippingWorkflow: Dispatching carrier for order {order.get('order_id')}")
            await workflow.execute_activity(
                dispatch_carrier_activity,
                args=[order],
                **activity_opts(),
            )

            self.state = "DONE"
            workflow.logger.info(f"ShippingWorkflow: Successfully completed for order {order.get('order_id')}")
            return "DISPATCHED"
        except Exception as e:
            self.last_error = str(e)
            workflow.logger.error(f"ShippingWorkflow: Failed with error: {e}")
            raise

    @workflow.query
    def status(self) -> dict:
        return {"state": self.state, "last_error": self.last_error}
    
@workflow.defn
class OrderWorkflow:
    def __init__(self) -> None:
        self.state: str = "INIT"
        self.last_error: Optional[str] = None
        self.order_cancelled: bool = False
        self.manual_review_approved: bool = False
        self.updated_address: Optional[dict] = None
        self.dispatch_failed_reason: Optional[str] = None

    @workflow.signal
    async def cancel_order(self) -> None:
        """Signal to cancel the order before shipment."""
        workflow.logger.info(f"OrderWorkflow: Received cancel_order signal in state {self.state}")
        if self.state not in ["SHIPPING", "MARKING_SHIPPED", "COMPLETED", "CHARGING_PAYMENT"]:
            self.order_cancelled = True
            workflow.logger.warning(f"OrderWorkflow: Order cancelled in state {self.state}")
        else:
            workflow.logger.warning(f"OrderWorkflow: Cannot cancel order in state {self.state}")

    @workflow.signal
    async def update_address(self, address: dict) -> None:
        """Signal to update shipping address prior to dispatch."""
        workflow.logger.info(f"OrderWorkflow: Received update_address signal: {address}")
        if self.state not in ["SHIPPING", "MARKING_SHIPPED", "COMPLETED"]:
            self.updated_address = address
            workflow.logger.info(f"OrderWorkflow: Address updated successfully")
        else:
            workflow.logger.warning(f"OrderWorkflow: Cannot update address in state {self.state}")

    @workflow.signal
    async def approve_order(self) -> None:
        """Signal to approve order after manual review."""
        workflow.logger.info(f"OrderWorkflow: Received approve_order signal")
        self.manual_review_approved = True

    @workflow.query
    def status(self) -> dict:
        return {
            "state": self.state,
            "last_error": self.last_error,
            "cancelled": self.order_cancelled,
            "updated_address": self.updated_address,
            "manual_review_approved": self.manual_review_approved,
        }

    @workflow.run
    async def run(
        self,
        order_id: str,
        payment_id: str,
        customer_id: str,
        customer_name: str,
        order_total: float = 0.0,
        priority: str = "NORMAL",
    ) -> str:
        workflow.logger.info(
            f"OrderWorkflow: Started for order_id={order_id}, payment_id={payment_id}, "
            f"customer_id={customer_id}, customer_name={customer_name}"
        )

        # Set search attributes for workflow discoverability
        workflow.upsert_search_attributes(
            [
                CUSTOMER_ID_ATTR.value_set(customer_id),
                CUSTOMER_NAME_ATTR.value_set(customer_name),
                ORDER_TOTAL_ATTR.value_set(order_total),
                PRIORITY_ATTR.value_set(priority),
            ]
        )

        try:
            # Step 1: receive
            self.state = "RECEIVING"
            workflow.logger.info(f"OrderWorkflow: State transition to RECEIVING")
            order = await workflow.execute_activity(
                receive_order_activity,
                args=[order_id, customer_id, order_total, priority],
                **activity_opts(),
            )

            if self.order_cancelled:
                self.state = "CANCELLED"
                workflow.logger.warning(f"OrderWorkflow: Cancelled after RECEIVING")
                return "CANCELLED"

            # Step 2: validate
            self.state = "VALIDATING"
            workflow.logger.info(f"OrderWorkflow: State transition to VALIDATING")
            await workflow.execute_activity(
                validate_order_activity,
                args=[order],
                **activity_opts(),
            )

            if self.order_cancelled:
                self.state = "CANCELLED"
                workflow.logger.warning(f"OrderWorkflow: Cancelled after VALIDATING")
                return "CANCELLED"

            # Step 2.5: Manual review timer - wait for approval signal
            self.state = "AWAITING_MANUAL_APPROVAL"
            workflow.logger.info(f"OrderWorkflow: State transition to AWAITING_MANUAL_APPROVAL - waiting for approve_order signal")

            # Wait for either approval or cancellation
            await workflow.wait_condition(
                lambda: self.manual_review_approved or self.order_cancelled,
                timeout=timedelta(seconds=30)  # 30 second timeout for manual approval
            )

            if self.order_cancelled:
                self.state = "CANCELLED"
                workflow.logger.warning(f"OrderWorkflow: Cancelled during manual review")
                return "CANCELLED"

            workflow.logger.info(f"OrderWorkflow: Manual review approved, proceeding to payment")

            # If address was updated, merge it into order
            if self.updated_address:
                order["address"] = self.updated_address
                workflow.logger.info(f"OrderWorkflow: Updated address applied to order")

            # Step 3: charge payment
            self.state = "CHARGING_PAYMENT"
            workflow.logger.info(f"OrderWorkflow: State transition to CHARGING_PAYMENT")
            await workflow.execute_activity(
                charge_payment_activity,
                args=[order, payment_id],
                **activity_opts(),
            )

            # After payment, we cannot cancel (too late - money charged)
            workflow.logger.info(f"OrderWorkflow: Payment charged successfully, order can no longer be cancelled")

            # Step 4: shipping as child workflow with retry logic
            self.state = "SHIPPING"
            workflow.logger.info(f"OrderWorkflow: State transition to SHIPPING - starting child workflow")

            max_shipping_retries = 3
            shipping_result = None

            for attempt in range(max_shipping_retries):
                try:
                    workflow.logger.info(f"OrderWorkflow: Attempting ShippingWorkflow (attempt {attempt + 1}/{max_shipping_retries})")
                    shipping_result = await workflow.execute_child_workflow(
                        ShippingWorkflow.run,
                        args=[order],
                        id=f"{order_id}-shipping-{attempt}",
                        task_queue="shipping-tq",  # Separate task queue for shipping
                    )
                    workflow.logger.info(f"OrderWorkflow: ShippingWorkflow completed successfully")
                    break  # Success, exit retry loop
                except ChildWorkflowError as e:
                    self.last_error = f"Shipping attempt {attempt + 1} failed: {str(e)}"
                    workflow.logger.error(f"OrderWorkflow: ShippingWorkflow failed on attempt {attempt + 1}: {e}")

                    if attempt < max_shipping_retries - 1:
                        workflow.logger.info(f"OrderWorkflow: Retrying ShippingWorkflow...")
                        await workflow.sleep(timedelta(seconds=2))  # Wait before retry
                    else:
                        workflow.logger.error(f"OrderWorkflow: ShippingWorkflow failed after {max_shipping_retries} attempts")
                        self.state = "SHIPPING_FAILED"
                        raise Exception(f"Shipping failed after {max_shipping_retries} attempts: {str(e)}")

            # Step 5: mark order shipped in DB
            self.state = "MARKING_SHIPPED"
            workflow.logger.info(f"OrderWorkflow: State transition to MARKING_SHIPPED")
            await workflow.execute_activity(
                mark_order_shipped_activity,
                args=[order],
                **activity_opts(),
            )

            self.state = "COMPLETED"
            workflow.logger.info(f"OrderWorkflow: Successfully completed for order {order_id}")
            return shipping_result

        except Exception as e:
            self.last_error = str(e)
            workflow.logger.error(f"OrderWorkflow: Failed with error: {e}")
            raise

