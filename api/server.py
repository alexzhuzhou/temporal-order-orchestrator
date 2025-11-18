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

from sqlalchemy import text

from temporal_app.config import TEMPORAL_HOST, ORDER_TASK_QUEUE
from temporal_app.workflows import OrderWorkflow
from temporal_app.db import SessionLocal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global Temporal client
temporal_client: Optional[Client] = None


# Pydantic models for request/response
class CreateCustomerRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class CustomerResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    created_at: str

class StartOrderRequest(BaseModel):
    customer_id: str
    customer_name: Optional[str] = None  # Optional, will be fetched if not provided
    payment_id: Optional[str] = None
    order_total: float = 100.0
    priority: str = "NORMAL"

class StartOrderResponse(BaseModel):
    order_id: str
    payment_id: str
    customer_id: str
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

class WorkflowSearchResult(BaseModel):
    workflow_id: str
    run_id: str
    status: str
    customer_id: str
    customer_name: str
    order_total: float
    priority: str
    start_time: str
    close_time: Optional[str] = None


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


# Customer Management Endpoints
@app.post("/customers", response_model=CustomerResponse)
async def create_customer(customer: CreateCustomerRequest):
    """
    Create a new customer

    - **name**: Customer's full name
    - **email**: Customer's email (must be unique)
    - **phone**: Optional phone number
    """
    customer_id = f"cust-{uuid.uuid4().hex[:8]}"

    try:
        with SessionLocal() as db, db.begin():
            db.execute(
                text("""
                    INSERT INTO customers (id, name, email, phone)
                    VALUES (:id, :name, :email, :phone)
                """),
                {
                    "id": customer_id,
                    "name": customer.name,
                    "email": customer.email,
                    "phone": customer.phone,
                },
            )

            result = db.execute(
                text("SELECT id, name, email, phone, created_at FROM customers WHERE id = :id"),
                {"id": customer_id}
            ).one()

        logger.info(f"✓ Customer created: {customer_id}")

        return CustomerResponse(
            id=result.id,
            name=result.name,
            email=result.email,
            phone=result.phone,
            created_at=str(result.created_at),
        )

    except Exception as e:
        logger.error(f"Failed to create customer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {str(e)}")


@app.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    """
    Get customer by ID

    - **customer_id**: Customer identifier
    """
    try:
        with SessionLocal() as db:
            result = db.execute(
                text("SELECT id, name, email, phone, created_at FROM customers WHERE id = :id"),
                {"id": customer_id}
            ).one_or_none()

        if not result:
            raise HTTPException(status_code=404, detail=f"Customer not found: {customer_id}")

        return CustomerResponse(
            id=result.id,
            name=result.name,
            email=result.email,
            phone=result.phone,
            created_at=str(result.created_at),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get customer: {str(e)}")


@app.get("/customers")
async def list_customers():
    """
    List all customers
    """
    try:
        with SessionLocal() as db:
            results = db.execute(
                text("SELECT id, name, email, phone, created_at FROM customers ORDER BY created_at DESC")
            ).fetchall()

        customers = [
            CustomerResponse(
                id=row.id,
                name=row.name,
                email=row.email,
                phone=row.phone,
                created_at=str(row.created_at),
            )
            for row in results
        ]

        return {"customers": customers, "count": len(customers)}

    except Exception as e:
        logger.error(f"Failed to list customers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list customers: {str(e)}")


# Start a new order workflow
@app.post("/orders/{order_id}/start", response_model=StartOrderResponse)
async def start_order(
    order_id: str,
    request: StartOrderRequest
):
    """
    Start a new OrderWorkflow

    - **order_id**: Unique order identifier (will be used as workflow ID)
    - **customer_id**: Customer identifier (required)
    - **customer_name**: Customer name (optional, fetched from DB if not provided)
    - **payment_id**: Optional payment identifier (auto-generated if not provided)
    - **order_total**: Total order amount (default: 100.0)
    - **priority**: Order priority: NORMAL, HIGH, URGENT (default: NORMAL)
    """
    if not temporal_client:
        raise HTTPException(status_code=500, detail="Temporal client not initialized")

    # Fetch customer name if not provided
    customer_name = request.customer_name
    if not customer_name:
        try:
            with SessionLocal() as db:
                result = db.execute(
                    text("SELECT name FROM customers WHERE id = :id"),
                    {"id": request.customer_id}
                ).one_or_none()

                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Customer not found: {request.customer_id}"
                    )

                customer_name = result.name
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch customer: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch customer: {str(e)}")

    # Generate payment_id if not provided
    payment_id = request.payment_id if request.payment_id else f"payment-{uuid.uuid4().hex[:8]}"

    logger.info(
        f"Starting OrderWorkflow for order_id={order_id}, customer_id={request.customer_id}, "
        f"customer_name={customer_name}, payment_id={payment_id}"
    )

    try:
        handle = await temporal_client.start_workflow(
            OrderWorkflow.run,
            args=[order_id, payment_id, request.customer_id, customer_name, request.order_total, request.priority],
            id=order_id,
            task_queue=ORDER_TASK_QUEUE,
            run_timeout=timedelta(seconds=15),
        )

        logger.info(f"✓ Workflow started: {handle.id}")

        return StartOrderResponse(
            order_id=order_id,
            payment_id=payment_id,
            customer_id=request.customer_id,
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


# Search/List workflows
@app.get("/orders")
async def list_workflows(
    customer_id: Optional[str] = None,
    customer_name: Optional[str] = None,
    priority: Optional[str] = None,
    min_total: Optional[float] = None,
    max_total: Optional[float] = None,
    limit: int = 50,
):
    """
    List and search workflows using Temporal search attributes

    Query parameters:
    - **customer_id**: Filter by customer ID (exact match)
    - **customer_name**: Filter by customer name (text search)
    - **priority**: Filter by priority (NORMAL, HIGH, URGENT)
    - **min_total**: Filter by minimum order total
    - **max_total**: Filter by maximum order total
    - **limit**: Maximum number of results (default: 50)
    """
    if not temporal_client:
        raise HTTPException(status_code=500, detail="Temporal client not initialized")

    try:
        # Build query string for Temporal
        query_parts = []

        if customer_id:
            query_parts.append(f'CustomerId = "{customer_id}"')

        if customer_name:
            query_parts.append(f'CustomerName = "{customer_name}"')

        if priority:
            query_parts.append(f'Priority = "{priority}"')

        if min_total is not None:
            query_parts.append(f'OrderTotal >= {min_total}')

        if max_total is not None:
            query_parts.append(f'OrderTotal <= {max_total}')

        # Combine query parts
        query = " AND ".join(query_parts) if query_parts else ""

        logger.info(f"Searching workflows with query: {query or '(no filters)'}")

        # Execute search
        workflows = []
        async for workflow_exec in temporal_client.list_workflows(query=query):
            # Extract search attributes
            search_attrs = workflow_exec.search_attributes or {}

            workflows.append(
                WorkflowSearchResult(
                    workflow_id=workflow_exec.id,
                    run_id=workflow_exec.run_id,
                    status=workflow_exec.status.name,
                    customer_id=search_attrs.get("CustomerId", [""])[0] if "CustomerId" in search_attrs else "",
                    customer_name=search_attrs.get("CustomerName", [""])[0] if "CustomerName" in search_attrs else "",
                    order_total=float(search_attrs.get("OrderTotal", [0.0])[0]) if "OrderTotal" in search_attrs else 0.0,
                    priority=search_attrs.get("Priority", [""])[0] if "Priority" in search_attrs else "",
                    start_time=str(workflow_exec.start_time),
                    close_time=str(workflow_exec.close_time) if workflow_exec.close_time else None,
                )
            )

            # Limit results
            if len(workflows) >= limit:
                break

        logger.info(f"✓ Found {len(workflows)} workflows")

        return {
            "workflows": workflows,
            "count": len(workflows),
            "query": query or "all workflows",
        }

    except Exception as e:
        logger.error(f"Failed to search workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search workflows: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
