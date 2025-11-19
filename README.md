# Temporal Order Orchestrator

A production-ready order orchestration system built with Temporal that demonstrates resilient workflow orchestration for e-commerce order processing with **signals**, **timers**, **retries**, **child workflows**, **separate task queues**, **search attributes**, and a **React frontend dashboard**.

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

✅ **Search Attributes & Advanced Queries**
- **CustomerId** (Keyword) - Exact customer matching
- **CustomerName** (Text) - Full-text customer search
- **OrderTotal** (Double) - Numeric range filtering
- **Priority** (Keyword) - Priority-based filtering (NORMAL, HIGH, URGENT)
- Powerful Temporal queries with combined filters
- Filter by customer, price ranges, and priority levels

✅ **Customer Management**
- Complete customer CRUD operations
- Customer database with name, email, phone
- Order-to-customer relationships with foreign keys
- Customer selection in order creation

✅ **React Frontend Dashboard**
- Real-time workflow monitoring with auto-refresh
- Interactive order creation form
- Customer management interface
- Advanced search and filtering UI
- Order timeline visualization
- Signal controls (approve, cancel, update address)
- Built-in documentation page

✅ **REST API**
- Start workflows with customer data
- Customer CRUD endpoints
- List/search workflows with filters
- Send signals (cancel, update address, approve)
- Query workflow status
- Get workflow results

✅ **Database Persistence**
- PostgreSQL for customers, orders, payments, events
- Normalized schema with foreign key constraints
- Idempotent payment processing
- Complete audit trail
- Indexed for query performance

✅ **Comprehensive Testing**
- Unit tests with Temporal's testing framework
- Integration tests
- API endpoint tests

---

## 🎨 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   React Frontend (Port 3000)                  │
│  Customer Management | Order Creation | Search & Filters     │
│  Real-time Monitoring | Signal Controls | Documentation      │
└──────────────────────────────────────────────────────────────┘
                            ↓ HTTP
┌──────────────────────────────────────────────────────────────┐
│                  FastAPI Server (Port 8000)                   │
│  Customer CRUD | Workflow Management | Signal Endpoints      │
└──────────────────────────────────────────────────────────────┘
                            ↓ gRPC
┌──────────────────────────────────────────────────────────────┐
│               Temporal Server (Port 7233/8080)                │
│  Workflow Orchestration | State Management | Search Attrs    │
└──────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────┐
        │                                   │
┌────────────────┐              ┌───────────────────┐
│ Order Worker   │              │ Shipping Worker   │
│  (order-tq)    │              │  (shipping-tq)    │
└────────────────┘              └───────────────────┘
        │                                   │
        ↓                                   ↓
┌──────────────────────────────────────────────────────────────┐
│               Business Logic & Activities                     │
│  Customer Management | Order Processing | Payment | Shipping │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                        │
│  Customers | Orders | Payments | Events                      │
└──────────────────────────────────────────────────────────────┘
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

### 3. Register Search Attributes

**Required for search/filtering functionality:**

```bash
# Windows:
scripts\setup_search_attributes.bat

# macOS/Linux:
bash scripts/setup_search_attributes.sh

# Or manually with tctl:
docker exec temporal tctl --address temporal:7233 admin cluster add-search-attributes \
  --name CustomerId --type Keyword
docker exec temporal tctl --address temporal:7233 admin cluster add-search-attributes \
  --name CustomerName --type Text
docker exec temporal tctl --address temporal:7233 admin cluster add-search-attributes \
  --name OrderTotal --type Double
docker exec temporal tctl --address temporal:7233 admin cluster add-search-attributes \
  --name Priority --type Keyword
```

> **Note:** You only need to do this once per Temporal cluster. See [SEARCH_ATTRIBUTES.md](SEARCH_ATTRIBUTES.md) for details.

### 4. Start Workers

In a new terminal (with virtual environment activated):

```bash
python -m temporal_app.worker_dev
```

This starts two workers:
- Order Worker listening on `order-tq`
- Shipping Worker listening on `shipping-tq`

### 5. Start API Server

In another terminal (with virtual environment activated):

```bash
python -m api.server
```

API will be available at: http://localhost:8000

### 6. Start React Frontend

In another terminal:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm start
```

Frontend will be available at: http://localhost:3000

**You're ready!** Open http://localhost:3000 in your browser to access the dashboard.

---

## 💻 Usage

### Option A: Using the React Frontend (Recommended)

The frontend provides a complete visual interface for managing orders and customers.

#### Access the Dashboard

Open http://localhost:3000 in your browser.

#### Create a Customer

1. Click "📋 View All Orders" from the home page
2. Click "👤 New Customer" button
3. Fill in customer details (name, email, phone)
4. Click "Create Customer"

#### Start a New Order

1. From the home page, fill in the order form:
   - **Customer**: Select from dropdown
   - **Order Total**: Enter amount (e.g., 100.00)
   - **Priority**: Choose NORMAL, HIGH, or URGENT
   - **Order ID & Payment ID**: Auto-generated (or customize)
2. Click "Start Order Workflow"
3. You'll be redirected to the order detail page

#### Monitor Order Progress

The order detail page shows:
- Real-time workflow status (auto-refreshes every 2 seconds)
- Order timeline with state transitions
- Signal controls (approve, cancel, update address)

#### Search and Filter Orders

1. Go to "📋 View All Orders"
2. Use the search filters:
   - **Customer**: Filter by specific customer
   - **Customer Name**: Text search for customer names
   - **Priority**: Filter by NORMAL, HIGH, or URGENT
   - **Price Range**: Set min/max order totals
3. Click "Search" to apply filters
4. View results in the table

#### Send Signals to Running Workflows

From the order detail page, use the signal buttons:
- **✅ Approve Order**: Approve manual review
- **❌ Cancel Order**: Cancel before payment
- **📍 Update Address**: Change shipping address

#### View Documentation

Click "📚 Documentation" from any page for complete platform guide.

---

### Option B: Using the CLI Tool

#### Start an Order

```bash
# Basic order (auto-creates customer)
python -m scripts.cli start

# With custom parameters
python -m scripts.cli start \
  --order-id order-123 \
  --payment-id payment-123 \
  --customer-id cust-001 \
  --customer-name "John Doe" \
  --order-total 250.00 \
  --priority HIGH
```

Output:
```
🚀 Starting OrderWorkflow
   Order ID: order-abc123
   Payment ID: payment-xyz789
   Customer: John Doe (cust-001)
   Total: $250.00
   Priority: HIGH

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

### Option C: Using the REST API

#### Start the API Server

```bash
python -m api.server
```

#### Create a Customer

```bash
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-0123"
  }'
```

Response:
```json
{
  "id": "cust-abc123",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "555-0123",
  "created_at": "2025-11-17T10:30:00"
}
```

#### Start an Order

```bash
curl -X POST http://localhost:8000/orders/order-001/start \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust-abc123",
    "payment_id": "payment-001",
    "order_total": 150.00,
    "priority": "HIGH"
  }'
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

#### List/Search Orders

```bash
# List all orders
curl http://localhost:8000/orders

# Filter by customer
curl http://localhost:8000/orders?customer_id=cust-abc123

# Filter by priority
curl http://localhost:8000/orders?priority=HIGH

# Filter by price range
curl "http://localhost:8000/orders?min_total=100&max_total=500"

# Combined filters
curl "http://localhost:8000/orders?customer_id=cust-abc123&priority=HIGH&min_total=100"
```

Response:
```json
{
  "workflows": [
    {
      "workflow_id": "order-001",
      "run_id": "abc123...",
      "status": "COMPLETED",
      "customer_id": "cust-abc123",
      "customer_name": "John Doe",
      "order_total": 150.00,
      "priority": "HIGH",
      "start_time": "2025-11-17T10:30:00",
      "close_time": "2025-11-17T10:35:00"
    }
  ],
  "count": 1,
  "query": "CustomerId = \"cust-abc123\" AND Priority = \"HIGH\" AND OrderTotal >= 100.0"
}
```

---

### Option D: Using Temporal UI

1. Open http://localhost:8080 in your browser
2. Navigate to **Workflows**
3. Find your workflow by ID (e.g., `order-abc123`)
4. Send signals using the UI's signal button

---

## 📚 API Reference

### Endpoints

#### Customer Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/customers` | Create a new customer |
| `GET` | `/customers` | List all customers |
| `GET` | `/customers/{customer_id}` | Get customer by ID |

#### Order Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/orders/{order_id}/start` | Start new order workflow (requires customer_id, order_total, priority) |
| `GET` | `/orders` | List/search workflows (supports filters: customer_id, customer_name, priority, min_total, max_total) |
| `GET` | `/orders/{order_id}/status` | Get workflow status |
| `GET` | `/orders/{order_id}/result` | Get workflow result (waits if running) |

#### Workflow Signals
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/orders/{order_id}/signals/approve` | Approve order (manual review) |
| `POST` | `/orders/{order_id}/signals/cancel` | Cancel order (before payment) |
| `POST` | `/orders/{order_id}/signals/update-address` | Update shipping address (before shipping) |

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

#### `customers`
```sql
CREATE TABLE customers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Stores customer information with unique email constraint.

#### `orders`
```sql
CREATE TABLE orders (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    state TEXT NOT NULL,
    address_json TEXT,
    order_total DECIMAL(10, 2) DEFAULT 0.00,
    priority TEXT DEFAULT 'NORMAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Indexes for query performance
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_state ON orders(state);
CREATE INDEX idx_orders_priority ON orders(priority);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

**States**: RECEIVED → VALIDATED → PAID → PACKAGE_PREPARED → CARRIER_DISPATCHED → SHIPPED

**Priorities**: NORMAL (default), HIGH, URGENT

#### `payments`
```sql
CREATE TABLE payments (
    payment_id TEXT PRIMARY KEY,  -- Idempotency key
    order_id TEXT NOT NULL,
    status TEXT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
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
│   ├── workflows.py                 # OrderWorkflow, ShippingWorkflow + search attributes
│   ├── activities.py                # Activity definitions
│   ├── functions.py                 # Business logic + customer management
│   ├── db.py                        # Database session factory
│   └── worker_dev.py                # Worker entry point (2 workers)
│
├── api/                             # REST API
│   └── server.py                    # FastAPI server + customer/search endpoints
│
├── frontend/                        # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── CustomerForm.jsx    # Customer creation form
│   │   │   ├── OrderForm.jsx       # Order creation form
│   │   │   ├── OrderSearch.jsx     # Search/filter interface
│   │   │   ├── OrderTimeline.jsx   # Visual workflow timeline
│   │   │   └── SignalButtons.jsx   # Signal controls
│   │   ├── pages/
│   │   │   ├── Home.jsx            # Landing page + order form
│   │   │   ├── Orders.jsx          # Orders dashboard with search
│   │   │   ├── OrderDetail.jsx     # Individual order view
│   │   │   └── Documentation.jsx   # Platform documentation
│   │   ├── services/
│   │   │   └── api.js              # API client with customer + order methods
│   │   ├── App.jsx                 # Router configuration
│   │   └── index.js                # Entry point
│   ├── package.json                # npm dependencies
│   └── tailwind.config.js          # Tailwind CSS config
│
├── scripts/                         # Utilities
│   ├── cli.py                       # CLI tool with customer support
│   ├── start_all.py                 # Startup script
│   ├── setup_search_attributes.py   # Python search attribute setup
│   ├── setup_search_attributes.sh   # Bash search attribute setup
│   └── setup_search_attributes.bat  # Windows search attribute setup
│
├── tests/                           # Tests
│   ├── test_workflows.py            # Workflow unit/integration tests
│   └── test_api.py                  # API endpoint tests
│
├── db/                              # Database
│   └── schema.sql                   # PostgreSQL schema (customers + orders + indexes)
│
├── docker-compose.yml               # All services (Temporal + DBs)
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Pytest configuration
├── .env.example                     # Environment template
├── SEARCH_ATTRIBUTES.md             # Search attributes guide
├── TESTING_GUIDE.md                 # Complete testing instructions
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
- Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
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
- [Search Attributes Guide](SEARCH_ATTRIBUTES.md) - Learn about our search attributes implementation
- [Testing Guide](TESTING_GUIDE.md) - Step-by-step testing instructions

---

## 🔍 Additional Features

### Search Attributes

This application implements Temporal's **Search Attributes** feature for powerful workflow querying:

- **CustomerId** (Keyword) - Filter workflows by exact customer ID
- **CustomerName** (Text) - Full-text search by customer name
- **OrderTotal** (Double) - Numeric range queries for order amounts
- **Priority** (Keyword) - Filter by order priority (NORMAL, HIGH, URGENT)

Search attributes enable:
- Complex queries with multiple filters
- Fast lookups using indexed fields
- Advanced workflow discovery in Temporal UI
- Programmatic workflow listing via API

See [SEARCH_ATTRIBUTES.md](SEARCH_ATTRIBUTES.md) for setup and usage details.

### React Frontend

The included React dashboard provides a complete UI for:
- Creating and managing customers
- Starting workflows with full parameter control
- Real-time workflow monitoring with auto-refresh
- Advanced search and filtering
- Sending signals to running workflows
- Built-in documentation and help

Access at: http://localhost:3000

---

**Built with ❤️ using Temporal Workflow Engine + FastAPI + React**
