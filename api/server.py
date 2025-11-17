"""
FastAPI server for Order Orchestration System
Provides REST API endpoints to trigger workflows and send signals
"""

import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from temporalio.client import Client, WorkflowHandle
from temporalio.service import RPCError

from temporal_app.config import TEMPORAL_HOST, ORDER_TASK_QUEUE
from temporal_app.workflows import OrderWorkflow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global Temporal client
temporal_client: Optional[Client] = None


# Pydantic models for request/response
class StartOrderRequest(BaseModel):
    payment_id: Optional[str] = None

class StartOrderResponse(BaseModel):
    order_id: str
    payment_id: str
    workflow_id: str
    run_id: str
    message: str

class UpdateAddressRequest(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"

class StatusResponse(BaseModel):
    order_id: str
    workflow_state: str
    is_running: bool
    status_details: Dict[str, Any]


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    global temporal_client
    logger.info(f"Connecting to Temporal at {TEMPORAL_HOST}")
    temporal_client = await Client.connect(TEMPORAL_HOST)
    logger.info("✓ Connected to Temporal successfully")

    yield

    # Shutdown
    logger.info("Shutting down API server")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Order Orchestration API",
    description="REST API for managing order workflows with Temporal",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper function to get workflow handle
async def get_workflow_handle(order_id: str) -> WorkflowHandle:
    """Get a workflow handle by order_id"""
    if not temporal_client:
        raise HTTPException(status_code=500, detail="Temporal client not initialized")

    try:
        handle = temporal_client.get_workflow_handle(order_id)
        return handle
    except Exception as e:
        logger.error(f"Failed to get workflow handle for {order_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Workflow not found: {order_id}")


# Root endpoint
@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "Order Orchestration API",
        "status": "running",
        "temporal_host": TEMPORAL_HOST,
        "task_queue": ORDER_TASK_QUEUE
    }


# Start a new order workflow
@app.post("/orders/{order_id}/start", response_model=StartOrderResponse)
async def start_order(
    order_id: str,
    request: StartOrderRequest = Body(default=None)
):
    """
    Start a new OrderWorkflow

    - **order_id**: Unique order identifier (will be used as workflow ID)
    - **payment_id**: Optional payment identifier (auto-generated if not provided)
    """
    if not temporal_client:
        raise HTTPException(status_code=500, detail="Temporal client not initialized")

    # Generate payment_id if not provided
    payment_id = request.payment_id if request and request.payment_id else f"payment-{uuid.uuid4().hex[:8]}"

    logger.info(f"Starting OrderWorkflow for order_id={order_id}, payment_id={payment_id}")

    try:
        handle = await temporal_client.start_workflow(
            OrderWorkflow.run,
            args=[order_id, payment_id],
            id=order_id,
            task_queue=ORDER_TASK_QUEUE,
            run_timeout=timedelta(seconds=15),
        )

        logger.info(f"✓ Workflow started: {handle.id}")

        return StartOrderResponse(
            order_id=order_id,
            payment_id=payment_id,
            workflow_id=handle.id,
            run_id=handle.result_run_id,
            message="Order workflow started successfully. Waiting for manual approval."
        )

    except Exception as e:
        logger.error(f"Failed to start workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")


# Send cancel signal
@app.post("/orders/{order_id}/signals/cancel")
async def cancel_order(order_id: str):
    """
    Send cancel_order signal to a running workflow

    - **order_id**: Order identifier (workflow ID)

    Note: Order can only be cancelled before payment is charged
    """
    logger.info(f"Sending cancel_order signal to {order_id}")

    try:
        handle = await get_workflow_handle(order_id)
        await handle.signal(OrderWorkflow.cancel_order)

        logger.info(f"✓ Cancel signal sent to {order_id}")

        return {
            "order_id": order_id,
            "signal": "cancel_order",
            "status": "sent",
            "message": "Cancellation signal sent successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send cancel signal: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send signal: {str(e)}")


# Send update address signal
@app.post("/orders/{order_id}/signals/update-address")
async def update_address(order_id: str, address: UpdateAddressRequest):
    """
    Send update_address signal to a running workflow

    - **order_id**: Order identifier (workflow ID)
    - **address**: New shipping address

    Note: Address can only be updated before shipping starts
    """
    logger.info(f"Sending update_address signal to {order_id}")

    address_dict = address.dict()

    try:
        handle = await get_workflow_handle(order_id)
        await handle.signal(OrderWorkflow.update_address, address_dict)

        logger.info(f"✓ Update address signal sent to {order_id}")

        return {
            "order_id": order_id,
            "signal": "update_address",
            "status": "sent",
            "address": address_dict,
            "message": "Address update signal sent successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send update address signal: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send signal: {str(e)}")


# Send approve signal
@app.post("/orders/{order_id}/signals/approve")
async def approve_order(order_id: str):
    """
    Send approve_order signal to continue workflow after manual review

    - **order_id**: Order identifier (workflow ID)

    This signal allows the workflow to proceed from AWAITING_MANUAL_APPROVAL to payment processing
    """
    logger.info(f"Sending approve_order signal to {order_id}")

    try:
        handle = await get_workflow_handle(order_id)
        await handle.signal(OrderWorkflow.approve_order)

        logger.info(f"✓ Approve signal sent to {order_id}")

        return {
            "order_id": order_id,
            "signal": "approve_order",
            "status": "sent",
            "message": "Approval signal sent successfully. Workflow will proceed to payment."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send approve signal: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send signal: {str(e)}")


# Query workflow status
@app.get("/orders/{order_id}/status", response_model=StatusResponse)
async def get_order_status(order_id: str):
    """
    Query the current status of an order workflow

    - **order_id**: Order identifier (workflow ID)

    Returns current workflow state, whether it's running, and detailed status information
    """
    logger.info(f"Querying status for {order_id}")

    try:
        handle = await get_workflow_handle(order_id)

        # Check if workflow is running
        is_running = False
        try:
            description = await handle.describe()
            is_running = description.status.name == "RUNNING"
        except Exception as e:
            logger.warning(f"Could not describe workflow: {e}")

        # Query the workflow status
        status_details = await handle.query(OrderWorkflow.status)

        logger.info(f"✓ Status retrieved for {order_id}: {status_details}")

        return StatusResponse(
            order_id=order_id,
            workflow_state=status_details.get("state", "UNKNOWN"),
            is_running=is_running,
            status_details=status_details
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query workflow status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to query status: {str(e)}")


# Get workflow result (if completed)
@app.get("/orders/{order_id}/result")
async def get_order_result(order_id: str):
    """
    Get the final result of a completed workflow

    - **order_id**: Order identifier (workflow ID)

    Note: This will wait for the workflow to complete if it's still running
    """
    logger.info(f"Getting result for {order_id}")

    try:
        handle = await get_workflow_handle(order_id)

        # This will wait for the workflow to complete
        result = await handle.result()

        logger.info(f"✓ Result retrieved for {order_id}: {result}")

        return {
            "order_id": order_id,
            "result": result,
            "message": "Workflow completed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get result: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
