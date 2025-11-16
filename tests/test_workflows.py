"""
Unit tests for workflows using Temporal's testing framework
"""

import pytest
from datetime import timedelta
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from temporalio.exceptions import WorkflowFailureError
from temporalio.client import WorkflowFailureError as ClientWorkflowFailureError

from temporal_app.workflows import OrderWorkflow, ShippingWorkflow
from temporal_app.activities import (
    receive_order_activity,
    validate_order_activity,
    charge_payment_activity,
    mark_order_shipped_activity,
    prepare_package_activity,
    dispatch_carrier_activity,
)


@pytest.fixture
async def workflow_env():
    """Create a test workflow environment"""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        yield env


@pytest.fixture
async def worker(workflow_env):
    """Create a test worker with all workflows and activities"""
    # Create workers for both task queues
    order_worker = Worker(
        workflow_env.client,
        task_queue="order-tq",
        workflows=[OrderWorkflow],
        activities=[
            receive_order_activity,
            validate_order_activity,
            charge_payment_activity,
            mark_order_shipped_activity,
        ],
    )

    shipping_worker = Worker(
        workflow_env.client,
        task_queue="shipping-tq",
        workflows=[ShippingWorkflow],
        activities=[
            prepare_package_activity,
            dispatch_carrier_activity,
        ],
    )

    # Run both workers
    async with order_worker, shipping_worker:
        yield order_worker


class TestOrderWorkflow:
    """Tests for OrderWorkflow"""

    @pytest.mark.asyncio
    async def test_successful_order_flow_with_approval(self, workflow_env, worker):
        """Test successful order flow with manual approval"""
        order_id = "test-order-001"
        payment_id = "test-payment-001"

        # Start the workflow
        handle = await workflow_env.client.start_workflow(
            OrderWorkflow.run,
            args=[order_id, payment_id],
            id=order_id,
            task_queue="order-tq",
            run_timeout=timedelta(seconds=15),
        )

        # Wait for workflow to reach manual approval state
        await workflow_env.sleep(1)

        # Check status - should be waiting for approval
        status = await handle.query(OrderWorkflow.status)
        assert status["state"] == "AWAITING_MANUAL_APPROVAL"
        assert not status["manual_review_approved"]

        # Send approval signal
        await handle.signal(OrderWorkflow.approve_order)

        # Wait for workflow to complete
        result = await handle.result()

        # Verify result
        assert result == "DISPATCHED"

        # Check final status
        final_status = await handle.query(OrderWorkflow.status)
        assert final_status["state"] == "COMPLETED"
        assert final_status["manual_review_approved"]
        assert not final_status["cancelled"]

    @pytest.mark.asyncio
    async def test_order_cancellation_before_approval(self, workflow_env, worker):
        """Test order cancellation before manual approval"""
        order_id = "test-order-002"
        payment_id = "test-payment-002"

        # Start the workflow
        handle = await workflow_env.client.start_workflow(
            OrderWorkflow.run,
            args=[order_id, payment_id],
            id=order_id,
            task_queue="order-tq",
            run_timeout=timedelta(seconds=15),
        )

        # Wait for workflow to reach manual approval state
        await workflow_env.sleep(1)

        # Send cancellation signal
        await handle.signal(OrderWorkflow.cancel_order)

        # Wait for workflow to complete
        result = await handle.result()

        # Verify cancellation
        assert result == "CANCELLED"

        # Check final status
        final_status = await handle.query(OrderWorkflow.status)
        assert final_status["state"] == "CANCELLED"
        assert final_status["cancelled"]

    @pytest.mark.asyncio
    async def test_address_update_before_approval(self, workflow_env, worker):
        """Test address update before manual approval"""
        order_id = "test-order-003"
        payment_id = "test-payment-003"

        # Start the workflow
        handle = await workflow_env.client.start_workflow(
            OrderWorkflow.run,
            args=[order_id, payment_id],
            id=order_id,
            task_queue="order-tq",
            run_timeout=timedelta(seconds=15),
        )

        # Wait for workflow to reach manual approval state
        await workflow_env.sleep(1)

        # Update address
        new_address = {
            "street": "456 New St",
            "city": "Boston",
            "state": "MA",
            "zip_code": "02101",
            "country": "USA"
        }
        await handle.signal(OrderWorkflow.update_address, new_address)

        # Check that address was updated
        status = await handle.query(OrderWorkflow.status)
        assert status["updated_address"] == new_address

        # Approve and complete
        await handle.signal(OrderWorkflow.approve_order)
        result = await handle.result()

        assert result == "DISPATCHED"

    @pytest.mark.asyncio
    async def test_cannot_cancel_after_payment(self, workflow_env, worker):
        """Test that order cannot be cancelled after payment is charged"""
        order_id = "test-order-004"
        payment_id = "test-payment-004"

        # Start the workflow
        handle = await workflow_env.client.start_workflow(
            OrderWorkflow.run,
            args=[order_id, payment_id],
            id=order_id,
            task_queue="order-tq",
            run_timeout=timedelta(seconds=15),
        )

        # Wait and approve
        await workflow_env.sleep(1)
        await handle.signal(OrderWorkflow.approve_order)

        # Wait for payment to be charged
        await workflow_env.sleep(2)

        # Check state - should be past CHARGING_PAYMENT
        status = await handle.query(OrderWorkflow.status)
        assert status["state"] in ["SHIPPING", "MARKING_SHIPPED", "COMPLETED"]

        # Try to cancel (should not work)
        await handle.signal(OrderWorkflow.cancel_order)

        # Wait for completion
        result = await handle.result()

        # Should complete successfully, not cancel
        assert result == "DISPATCHED"

        final_status = await handle.query(OrderWorkflow.status)
        assert final_status["state"] == "COMPLETED"
        assert not final_status["cancelled"]  # Should NOT be cancelled

    @pytest.mark.asyncio
    async def test_manual_approval_timeout(self, workflow_env, worker):
        """Test that workflow times out if manual approval not received"""
        order_id = "test-order-005"
        payment_id = "test-payment-005"

        # Start the workflow
        handle = await workflow_env.client.start_workflow(
            OrderWorkflow.run,
            args=[order_id, payment_id],
            id=order_id,
            task_queue="order-tq",
            run_timeout=timedelta(seconds=15),
        )

        # Wait for workflow to reach manual approval state
        await workflow_env.sleep(1)

        # Don't send approval - let it timeout
        # Skip time to trigger the 30-second approval timeout
        await workflow_env.sleep(31)

        # Workflow should timeout
        with pytest.raises((WorkflowFailureError, ClientWorkflowFailureError)):
            await handle.result()


class TestShippingWorkflow:
    """Tests for ShippingWorkflow"""

    @pytest.mark.asyncio
    async def test_successful_shipping(self, workflow_env, worker):
        """Test successful shipping workflow"""
        order = {
            "order_id": "test-order-shipping-001",
            "items": [{"sku": "ABC", "qty": 1}]
        }

        # Start the shipping workflow
        handle = await workflow_env.client.start_workflow(
            ShippingWorkflow.run,
            args=[order],
            id=f"{order['order_id']}-shipping",
            task_queue="shipping-tq",
        )

        # Wait for completion
        result = await handle.result()

        # Verify result
        assert result == "DISPATCHED"

        # Check final status
        status = await handle.query(ShippingWorkflow.status)
        assert status["state"] == "DONE"
        assert status["last_error"] is None


class TestIntegration:
    """Integration tests for the full order flow"""

    @pytest.mark.asyncio
    async def test_complete_order_lifecycle(self, workflow_env, worker):
        """Test complete order lifecycle from start to finish"""
        order_id = "test-integration-001"
        payment_id = "test-integration-payment-001"

        # Start the workflow
        handle = await workflow_env.client.start_workflow(
            OrderWorkflow.run,
            args=[order_id, payment_id],
            id=order_id,
            task_queue="order-tq",
            run_timeout=timedelta(seconds=15),
        )

        # Wait and check status at each stage
        await workflow_env.sleep(0.5)
        status1 = await handle.query(OrderWorkflow.status)
        assert status1["state"] in ["RECEIVING", "VALIDATING", "AWAITING_MANUAL_APPROVAL"]

        # Wait for manual approval state
        await workflow_env.sleep(1)
        status2 = await handle.query(OrderWorkflow.status)
        assert status2["state"] == "AWAITING_MANUAL_APPROVAL"

        # Approve
        await handle.signal(OrderWorkflow.approve_order)

        # Wait for payment
        await workflow_env.sleep(1)
        status3 = await handle.query(OrderWorkflow.status)
        assert status3["state"] in ["CHARGING_PAYMENT", "SHIPPING", "MARKING_SHIPPED", "COMPLETED"]

        # Wait for completion
        result = await handle.result()

        # Verify
        assert result == "DISPATCHED"

        final_status = await handle.query(OrderWorkflow.status)
        assert final_status["state"] == "COMPLETED"
        assert final_status["manual_review_approved"]
        assert not final_status["cancelled"]

    @pytest.mark.asyncio
    async def test_order_with_address_update_and_approval(self, workflow_env, worker):
        """Test order with both address update and approval"""
        order_id = "test-integration-002"
        payment_id = "test-integration-payment-002"

        # Start workflow
        handle = await workflow_env.client.start_workflow(
            OrderWorkflow.run,
            args=[order_id, payment_id],
            id=order_id,
            task_queue="order-tq",
            run_timeout=timedelta(seconds=15),
        )

        # Wait for manual approval state
        await workflow_env.sleep(1)

        # Update address
        new_address = {
            "street": "789 Test Ave",
            "city": "Seattle",
            "state": "WA",
            "zip_code": "98101",
            "country": "USA"
        }
        await handle.signal(OrderWorkflow.update_address, new_address)

        # Verify address updated
        status = await handle.query(OrderWorkflow.status)
        assert status["updated_address"] == new_address

        # Approve
        await handle.signal(OrderWorkflow.approve_order)

        # Complete workflow
        result = await handle.result()
        assert result == "DISPATCHED"

        # Verify final state
        final_status = await handle.query(OrderWorkflow.status)
        assert final_status["state"] == "COMPLETED"
        assert final_status["updated_address"] == new_address


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
