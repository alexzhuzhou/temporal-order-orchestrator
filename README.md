# Temporal Order Orchestrator

A production-ready order orchestration system built with Temporal that demonstrates resilient workflow orchestration for e-commerce order processing with **signals**, **timers**, **retries**, **child workflows**, and **separate task queues**.

## 🎯 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 📋 Overview

This application demonstrates a complete order processing workflow using Temporal's workflow orchestration capabilities. The system handles the full order lifecycle: order receipt → validation → **manual approval** → payment → shipping → completion.

### Key Features

✅ **Workflow Signals**
- `CancelOrder` - Cancel orders before payment
- `UpdateAddress` - Update shipping address before dispatch
- `ApproveOrder` - Manual approval after validation

✅ **Manual Review Timer**
- Workflow pauses after validation
- Waits for human approval signal (30-second timeout)
- Can be cancelled during review

✅ **Retry Logic**
- Parent workflow retries child workflow up to 3 times
- 2-second delay between retries
- Graceful error handling and logging

✅ **Separate Task Queues**
- `order-tq` for OrderWorkflow
- `shipping-tq` for ShippingWorkflow
- Demonstrates queue isolation

✅ **REST API**
- Start workflows
- Send signals (cancel, update address, approve)
- Query workflow status
- Get workflow results

✅ **Database Persistence**
- PostgreSQL for order/payment/event tracking
- Idempotent payment processing
- Complete audit trail

✅ **Comprehensive Testing**
- Unit tests with Temporal's testing framework
- Integration tests
- API endpoint tests

---

## 🎨 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                             │
│  (REST API / CLI / Direct Client)                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Temporal Server                             │
│  (Workflow orchestration, state management)                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌──────────────────────────────────┐
        │                                  │
┌───────────────┐              ┌──────────────────┐
│ Order Worker  │              │ Shipping Worker  │
│  (order-tq)   │              │  (shipping-tq)   │
└───────────────┘              └──────────────────┘
        │                                  │
        ↓                                  ↓
┌─────────────────────────────────────────────────────────────┐
│              Business Logic & Activities                     │
│  (Order processing, payment, shipping)                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                         │
│  (Orders, Payments, Events)                                 │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Flow

```
START
  ↓
[1] RECEIVING → receive_order
  ↓
[2] VALIDATING → validate_order
  ↓
[3] AWAITING_MANUAL_APPROVAL ⏰
    └─ Wait for approve_order signal (30s timeout)
    └─ Can accept update_address signal
    └─ Can accept cancel_order signal
  ↓
[4] CHARGING_PAYMENT → charge_payment (idempotent)
  ↓
[5] SHIPPING → Child Workflow on shipping-tq
    ├─ prepare_package
    └─ dispatch_carrier
    └─ Retry up to 3 times on failure
  ↓
[6] MARKING_SHIPPED → mark_order_shipped
  ↓
COMPLETED ✓
```

---

## 🚀 Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop/))
- **Git** (for cloning the repository)

---

## ⚡ Quick Start

### 1. Clone and Install

```bash
git clone <repository-url>
cd temporal-order-orchestrator

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start All Services

```bash
# Start Docker services (Temporal + Databases)
docker-compose up -d

# Wait ~30 seconds for services to be ready
```

This starts:
- **Application Database** (PostgreSQL on port 5432)
- **Temporal Database** (PostgreSQL on port 5433)
- **Temporal Server** (gRPC on port 7233)
- **Temporal UI** (Web on port 8080)

### 3. Start Workers

In a new terminal (with virtual environment activated):

```bash
python -m temporal_app.worker_dev
```

This starts two workers:
- Order Worker listening on `order-tq`
- Shipping Worker listening on `shipping-tq`

### 4. (Optional) Start API Server

In another terminal (with virtual environment activated):

```bash
python -m api.server
```

API will be available at: http://localhost:8000

---

## 💻 Usage

### Option A: Using the CLI Tool (Recommended)

#### Start an Order

```bash
python -m scripts.cli start
```

Output:
```
🚀 Starting OrderWorkflow
   Order ID: order-abc123
   Payment ID: payment-xyz789

⏳ Workflow is now waiting for manual approval...

To approve this order, run:
   python -m scripts.cli approve order-abc123
```

#### Approve the Order

```bash
python -m scripts.cli approve order-abc123
```

#### Check Order Status

```bash
python -m scripts.cli status order-abc123
```

Output:
```
📊 Workflow Status:
   Status: RUNNING

📋 Order Details:
   State: CHARGING_PAYMENT
   Cancelled: False
   Manual Review Approved: True
```

#### Cancel an Order (before payment)

```bash
python -m scripts.cli cancel order-abc123
```

#### Update Shipping Address (before shipping)

```bash
python -m scripts.cli update-address order-abc123 "456 New St" "Boston" "MA" "02101"
```

#### Wait for Workflow Result

```bash
python -m scripts.cli wait order-abc123
```

### Option B: Using the REST API

#### Start the API Server

```bash
python -m api.server
```

#### Start an Order

```bash
curl -X POST http://localhost:8000/orders/order-001/start \
  -H "Content-Type: application/json" \
  -d '{"payment_id": "payment-001"}'
```

#### Approve Order

```bash
curl -X POST http://localhost:8000/orders/order-001/signals/approve
```

#### Update Address

```bash
curl -X POST http://localhost:8000/orders/order-001/signals/update-address \
  -H "Content-Type: application/json" \
  -d '{
    "street": "456 New St",
    "city": "Boston",
    "state": "MA",
    "zip_code": "02101",
    "country": "USA"
  }'
```

#### Cancel Order

```bash
curl -X POST http://localhost:8000/orders/order-001/signals/cancel
```

#### Get Order Status

```bash
curl http://localhost:8000/orders/order-001/status
```

#### Get Workflow Result

```bash
curl http://localhost:8000/orders/order-001/result
```

### Option C: Using Temporal UI

1. Open http://localhost:8080 in your browser
2. Navigate to **Workflows**
3. Find your workflow by ID (e.g., `order-abc123`)
4. Send signals using the UI's signal button

---

## 📚 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/orders/{order_id}/start` | Start new order workflow |
| `POST` | `/orders/{order_id}/signals/cancel` | Cancel order |
| `POST` | `/orders/{order_id}/signals/update-address` | Update shipping address |
| `POST` | `/orders/{order_id}/signals/approve` | Approve order (manual review) |
| `GET` | `/orders/{order_id}/status` | Get workflow status |
| `GET` | `/orders/{order_id}/result` | Get workflow result (waits if running) |

### API Documentation

Visit http://localhost:8000/docs for interactive Swagger documentation.

---

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Workflow tests
pytest tests/test_workflows.py -v

# API tests
pytest tests/test_api.py -v
```

### Run Tests with Coverage

```bash
pytest --cov=temporal_app --cov=api --cov-report=html
```

### Test Categories

- **Unit Tests**: Test workflows in isolation using Temporal's testing framework
- **Integration Tests**: Test complete order lifecycle
- **API Tests**: Test REST API endpoints

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# Temporal Configuration
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default

# Database Configuration
DB_USER=trellis
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trellis
```

### Task Queues

Configured in `temporal_app/config.py`:

```python
ORDER_TASK_QUEUE = "order-tq"      # For OrderWorkflow
SHIPPING_TASK_QUEUE = "shipping-tq"  # For ShippingWorkflow
```

### Activity Timeouts

Configured in `temporal_app/activities.py`:

```python
ACTIVITY_SCHEDULE_TO_CLOSE = timedelta(seconds=4)
ACTIVITY_START_TO_CLOSE = timedelta(seconds=4)
```

### Workflow Timeout

```python
run_timeout = timedelta(seconds=15)  # Total workflow must complete in 15 seconds
```

---

## 🗄️ Database Schema

### Tables

#### `orders`
```sql
CREATE TABLE orders (
    id TEXT PRIMARY KEY,
    state TEXT NOT NULL,
    address_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**States**: RECEIVED → VALIDATED → PAID → PACKAGE_PREPARED → CARRIER_DISPATCHED → SHIPPED

#### `payments`
```sql
CREATE TABLE payments (
    payment_id TEXT PRIMARY KEY,  -- Idempotency key
    order_id TEXT NOT NULL,
    status TEXT NOT NULL,
    amount INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `events`
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    order_id TEXT NOT NULL,
    type TEXT NOT NULL,
    payload_json TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Idempotency

Payment processing is **idempotent** using `payment_id` as the idempotency key:

```python
# Check if payment already processed
existing = db.execute(
    "SELECT status, amount FROM payments WHERE payment_id = :pid",
    {"pid": payment_id}
).one_or_none()

if existing:
    return {"status": existing.status, "amount": existing.amount}  # Safe retry
```

---

## 🎯 Key Features Explained

### 1. Signals

Signals allow external systems to communicate with running workflows.

**CancelOrder**
- Can cancel before payment is charged
- Sets `order_cancelled = True`
- Workflow exits gracefully with "CANCELLED" status

**UpdateAddress**
- Can update before shipping starts
- Merges new address into order
- Applied before child workflow starts

**ApproveOrder**
- Required after validation
- Allows workflow to proceed to payment
- Timeout: 30 seconds

### 2. Manual Review Timer

```python
self.state = "AWAITING_MANUAL_APPROVAL"

# Wait for approval signal
await workflow.wait_condition(
    lambda: self.manual_review_approved or self.order_cancelled,
    timeout=timedelta(seconds=30)
)
```

### 3. Child Workflow with Retries

```python
max_shipping_retries = 3

for attempt in range(max_shipping_retries):
    try:
        result = await workflow.execute_child_workflow(
            ShippingWorkflow.run,
            args=[order],
            task_queue="shipping-tq",
        )
        break  # Success
    except ChildWorkflowError as e:
        if attempt < max_shipping_retries - 1:
            await workflow.sleep(timedelta(seconds=2))  # Retry delay
        else:
            raise  # Failed after all retries
```

### 4. Structured Logging

All state transitions, retries, and errors are logged:

```python
workflow.logger.info(f"OrderWorkflow: State transition to CHARGING_PAYMENT")
workflow.logger.error(f"OrderWorkflow: ShippingWorkflow failed on attempt {attempt + 1}")
```

---

## 🛠️ Troubleshooting

### Issue: Workers not picking up tasks

**Solution**: Verify task queues match
```python
# In workflow:
task_queue=ORDER_TASK_QUEUE  # Should be "order-tq"

# In worker:
task_queue=ORDER_TASK_QUEUE  # Should match
```

### Issue: Workflow times out waiting for approval

**Solution**: Send approval signal within 30 seconds
```bash
python -m scripts.cli approve <order_id>
```

### Issue: Database connection error

**Solution**: Check Docker services are running
```bash
docker-compose ps
docker-compose logs db
```

### Issue: Temporal server not responding

**Solution**: Check Temporal is healthy
```bash
docker-compose ps temporal
docker-compose logs temporal
```

### View All Logs

```bash
# Application logs
docker-compose logs -f

# Specific service
docker-compose logs -f temporal
docker-compose logs -f db
```

---

## 📦 Project Structure

```
temporal-order-orchestrator/
│
├── temporal_app/                    # Main application
│   ├── config.py                    # Configuration (env vars, task queues)
│   ├── workflows.py                 # OrderWorkflow, ShippingWorkflow
│   ├── activities.py                # Activity definitions
│   ├── functions.py                 # Business logic
│   ├── db.py                        # Database session factory
│   └── worker_dev.py                # Worker entry point (2 workers)
│
├── api/                             # REST API
│   └── server.py                    # FastAPI server
│
├── scripts/                         # Utilities
│   ├── cli.py                       # CLI tool
│   ├── start_all.py                 # Startup script
│   └── run_order_once.py            # Simple workflow trigger
│
├── tests/                           # Tests
│   ├── test_workflows.py            # Workflow unit/integration tests
│   └── test_api.py                  # API endpoint tests
│
├── db/                              # Database
│   └── schema.sql                   # PostgreSQL schema
│
├── docker-compose.yml               # All services (Temporal + DBs)
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Pytest configuration
├── .env.example                     # Environment template
└── README.md                        # This file
```

---

## 🔒 Security

- ✅ Environment variables for credentials
- ✅ `.env` excluded from git
- ✅ Idempotent payment processing
- ✅ Database transactions (ACID)
- ✅ Input validation on API endpoints

**Production Recommendations:**
- Use strong, randomly generated passwords
- Enable Temporal TLS
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- Implement API authentication/authorization
- Enable rate limiting

---

## 📞 Support

For issues or questions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review Temporal logs: `docker-compose logs temporal`
- Open an issue on GitHub

---

## 📄 License

This project is provided as-is for demonstration purposes.

---

## 🎓 Learning Resources

- [Temporal Documentation](https://docs.temporal.io/)
- [Temporal Python SDK](https://github.com/temporalio/sdk-python)
- [Temporal Samples](https://github.com/temporalio/samples-python)

---

**Built with ❤️ using Temporal Workflow Engine**
