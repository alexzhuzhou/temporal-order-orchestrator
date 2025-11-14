# Temporal Order Orchestrator

A production-ready order orchestration system built with Temporal that demonstrates resilient workflow orchestration for e-commerce order processing. This system handles the complete order lifecycle from receipt through validation, payment processing, and shipping coordination.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Running the Application](#running-the-application)
- [Testing Workflows](#testing-workflows)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Development](#development)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Overview

This application demonstrates a multi-step order processing workflow using Temporal's workflow orchestration capabilities. Key features include:

- **Resilient workflow execution** with automatic retries and timeout handling
- **Parent-child workflow coordination** for shipping operations
- **Idempotent payment processing** to handle retries safely
- **Database state tracking** with PostgreSQL
- **Event logging** for complete audit trails
- **Intentional flakiness** for testing resilience (configurable)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop/))
- **Temporal CLI** ([Installation Guide](https://docs.temporal.io/cli))
- **Git** (for cloning the repository)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd temporal-order-orchestrator
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

**Activate the virtual environment:**

- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

- **Windows (Command Prompt):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

- **macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional for Development)

For development, you can use the default settings. For production or custom configuration:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your passwords (required for production!)
# DB_PASSWORD=your_secure_password_here
```

**Security Note:** Never commit `.env` files to version control. See [SECURITY.md](SECURITY.md) for more details.

### 5. Start PostgreSQL Database

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL on port 5432
- Automatically create the database schema
- Use default credentials for development (username: `trellis`, password: `trellis`)

**Verify the database is running:**

```bash
docker ps
```

You should see `temporal-order-orchestrator-db-1` with status "Up".

**Security Warning:** The default password is `trellis` for development convenience. For production, always set `DB_PASSWORD` environment variable before running docker-compose. See [SECURITY.md](SECURITY.md).

### 6. Start Temporal Server

**Option A: Using Temporal CLI (Recommended for development)**

```bash
temporal server start-dev
```

This starts a local Temporal server on `localhost:7233` with a Web UI at `http://localhost:8233`.

**Option B: Using Docker**

```bash
docker run -p 7233:7233 -p 8233:8233 temporalio/auto-setup:latest
```

## Quick Start

Once all prerequisites are installed and services are running:

```bash
# Terminal 1: Start the Temporal worker
python -m temporal_app.worker_dev

# Terminal 2: Run a test workflow
python -m scripts.run_order_once
```

## Running the Application

### Step 1: Start the Worker

The worker processes workflow and activity tasks. In a terminal:

```bash
python -m temporal_app.worker_dev
```

**Expected output:**
- The worker connects to Temporal server at `localhost:7233`
- It registers workflows: `OrderWorkflow`, `ShippingWorkflow`
- It registers 6 activities for order processing
- The terminal will be silent while waiting for work

**Keep this terminal running** - the worker must be active to process workflows.

### Step 2: Submit a Workflow

In a **new terminal** (with the virtual environment activated):

```bash
python -m scripts.run_order_once
```

This script:
- Generates a unique order ID and payment ID
- Starts an `OrderWorkflow` in Temporal
- Waits for the workflow to complete
- Prints the final result and status

**Example output:**

```
Started workflow: order-a1b2c3d4 019a8ea5-b067-77be-9fdb-213c4764eba0
Workflow result: DISPATCHED
Final status: {'state': 'COMPLETED', 'last_error': None}
```

### Step 3: Monitor in Temporal UI

Open your browser to **http://localhost:8233** to access the Temporal Web UI.

You can:
- View workflow execution history
- See activity retries and timeouts
- Query workflow state
- Monitor worker health
- View event logs

## Testing Workflows

### Running Multiple Workflows

Each execution of `run_order_once.py` creates a unique workflow:

```bash
python -m scripts.run_order_once  # Creates order-abc123
python -m scripts.run_order_once  # Creates order-def456
python -m scripts.run_order_once  # Creates order-ghi789
```

### Understanding Flaky Behavior

The system includes **intentional flakiness** to demonstrate Temporal's resilience features. Each activity has a 33% chance of:

1. **Immediate error** - Raises `RuntimeError`
2. **Timeout** - Sleeps for 300 seconds (activity times out at 4 seconds)
3. **Success** - Completes immediately

This means workflows will often fail and retry. Watch the Temporal UI to see:
- Activity retries with exponential backoff
- Timeout handling
- Workflow recovery

### Disabling Flakiness for Testing

To see successful end-to-end execution without retries, edit `temporal_app/functions.py`:

```python
async def flaky_call() -> None:
    """Either raise an error or sleep long enough to trigger an activity timeout."""
    return  # Always succeed - comment out the random logic below

    # rand_num = random.random()
    # if rand_num < 0.33:
    #     raise RuntimeError("Forced failure for testing")
    # ...
```

**Remember to restart the worker** after making changes:
- Press `Ctrl+C` in the worker terminal
- Run `python -m temporal_app.worker_dev` again

## Project Structure

```
temporal-order-orchestrator/
├── temporal_app/
│   ├── __init__.py
│   ├── activities.py      # Activity definitions (thin wrappers)
│   ├── workflows.py       # Workflow definitions (OrderWorkflow, ShippingWorkflow)
│   ├── functions.py       # Business logic with intentional flakiness
│   ├── db.py             # Database session management
│   ├── config.py         # Configuration (Temporal host, DB URL)
│   └── worker_dev.py     # Worker entry point
├── scripts/
│   ├── init_db.py        # Manual database initialization
│   ├── run_order_once.py # Test script to start workflows
│   └── test_db.py        # Database connection testing
├── db/
│   └── schema.sql        # PostgreSQL schema (orders, payments, events)
├── docker-compose.yml    # PostgreSQL service definition
├── requirements.txt      # Python dependencies
├── CLAUDE.md            # Detailed architecture documentation
└── README.md            # This file
```

## How It Works

### Workflow Orchestration

#### OrderWorkflow

The main orchestrator that coordinates the entire order fulfillment process:

1. **Receive Order** - Creates order record in database (state: RECEIVED)
2. **Validate Order** - Validates order data (state: VALIDATED)
3. **Charge Payment** - Processes payment with idempotency (state: PAID)
4. **Shipping** - Spawns child `ShippingWorkflow` (state: SHIPPING)
5. **Mark Shipped** - Updates order status (state: SHIPPED)
6. **Complete** - Workflow completes successfully

**Location:** `temporal_app/workflows.py:49-105`

#### ShippingWorkflow

Child workflow that handles physical shipping operations:

1. **Prepare Package** - Prepares items for shipping
2. **Dispatch Carrier** - Sends package to shipping carrier
3. **Return Status** - Returns "DISPATCHED" to parent workflow

**Location:** `temporal_app/workflows.py:19-46`

### Activity Layer

Activities are thin wrappers around business logic:

- All activities have **4-second timeouts** (schedule-to-close and start-to-close)
- Activities automatically retry on failure (Temporal default retry policy)
- Each activity calls the corresponding function in `functions.py`

**Location:** `temporal_app/activities.py`

### Business Logic Layer

Core business functions implement order processing:

- **`order_received()`** - Creates order record and event
- **`order_validated()`** - Validates order and updates state
- **`payment_charged()`** - Charges payment with idempotency key
- **`package_prepared()`** - Marks package as prepared
- **`carrier_dispatched()`** - Marks package as dispatched
- **`order_shipped()`** - Marks order as shipped

All functions:
- Call `flaky_call()` first to simulate failures
- Perform database writes to track state
- Emit events for audit trails

**Location:** `temporal_app/functions.py`

### Database Schema

Three core tables:

- **`orders`** - Tracks order state transitions (RECEIVED → VALIDATED → PAID → SHIPPED)
- **`payments`** - Stores payment records with idempotency key (`payment_id`)
- **`events`** - Event log for all order-related actions with JSON payloads

**Location:** `db/schema.sql`

### Idempotency

The `payment_charged()` function demonstrates critical idempotency handling:

```python
# Check if payment_id already exists
row = db.execute(
    text("SELECT status, amount FROM payments WHERE payment_id = :pid"),
    {"pid": payment_id},
).one_or_none()

if row:
    # Return existing result - safe for retries
    return {"status": row.status, "amount": row.amount}

# First time - process payment
# ...
```

This ensures that even if Temporal retries the activity, the payment is only charged once.

**Location:** `temporal_app/functions.py:78-133`

## Troubleshooting

### Worker Not Starting

**Problem:** `ModuleNotFoundError: No module named 'temporal_app'`

**Solution:**
```bash
# Ensure you're using the -m flag:
python -m temporal_app.worker_dev

# NOT: python temporal_app/worker_dev.py
```

### Database Connection Failed

**Problem:** `FATAL: password authentication failed for user "trellis"`

**Possible causes:**

1. **Another PostgreSQL instance is running on port 5432**

   **Solution:** Stop other PostgreSQL services:
   ```bash
   # Windows
   net stop postgresql-x64-17

   # Disable auto-start
   sc config postgresql-x64-17 start=disabled
   ```

2. **Docker database was created with different credentials**

   **Solution:** Recreate the database:
   ```bash
   docker-compose down -v  # Remove old volume
   docker-compose up -d     # Start fresh
   ```

### Workflow Fails Immediately

**Problem:** `TypeError: execute_activity() takes from 1 to 2 positional arguments...`

**Cause:** Code was updated while old workflows were running. Temporal replays workflows from history.

**Solution:** Start a new workflow with a new ID (the script does this automatically):
```bash
python -m scripts.run_order_once
```

### Temporal Server Not Running

**Problem:** Worker shows connection timeout or `Connection refused`

**Solution:** Start the Temporal server:
```bash
temporal server start-dev
```

**Verify it's running:**
- Visit http://localhost:8233 in your browser
- You should see the Temporal Web UI

### All Workflows Timing Out

**Problem:** Every workflow times out even after multiple retries

**Cause:** The flaky_call() function has a 67% failure rate (33% error + 33% timeout)

**Solution:** Either:

1. **Wait for retries** - Eventually one will succeed (Temporal will keep retrying)
2. **Disable flakiness temporarily** - See "Disabling Flakiness for Testing" section above
3. **Increase the run timeout** in `scripts/run_order_once.py`:
   ```python
   run_timeout=timedelta(seconds=300)  # Increase from 15 to 300
   ```

### Database Schema Not Created

**Problem:** SQL errors about missing tables

**Solution:** Manually initialize the schema:
```bash
python scripts/init_db.py
```

Or ensure docker-compose mounted the schema:
```bash
docker-compose down
docker-compose up -d
docker logs temporal-order-orchestrator-db-1
# Should see: "CREATE TABLE" messages
```

## Additional Resources

- **Temporal Documentation:** https://docs.temporal.io/
- **Temporal Python SDK:** https://docs.temporal.io/dev-guide/python
- **Project Architecture:** See `CLAUDE.md` for detailed implementation notes

## Configuration

### Environment Variables

You can customize behavior with environment variables:

```bash
# Temporal configuration
export TEMPORAL_HOST="localhost:7233"
export TEMPORAL_NAMESPACE="default"

# Database configuration
export DB_PASSWORD="your_secure_password"
export DB_URL="postgresql+psycopg2://trellis:${DB_PASSWORD}@localhost:5432/trellis"
```

Or use individual components:
```bash
export DB_USER="trellis"
export DB_PASSWORD="your_secure_password"
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="trellis"
```

### Activity Timeouts

To adjust activity timeouts, edit `temporal_app/activities.py`:

```python
ACTIVITY_SCHEDULE_TO_CLOSE = timedelta(seconds=4)  # Change as needed
ACTIVITY_START_TO_CLOSE = timedelta(seconds=4)     # Change as needed
```

**Remember to restart the worker** after making changes.

## Development

### Adding New Activities

1. Add business logic function to `temporal_app/functions.py`
2. Create activity wrapper in `temporal_app/activities.py`
3. Register activity in `temporal_app/worker_dev.py`
4. Use in workflow via `workflow.execute_activity()`

### Adding New Workflows

1. Create workflow class in `temporal_app/workflows.py`
2. Decorate class with `@workflow.defn`
3. Add `@workflow.run` method
4. Register in `temporal_app/worker_dev.py`

## Security

### Important Security Considerations

This application follows security best practices for handling sensitive information:

#### No Hardcoded Credentials

All sensitive credentials are managed through environment variables:
- Database passwords
- API keys (if added in future)
- Connection strings

#### Development vs Production

**Development Mode:**
- Uses default password (`trellis`) if `DB_PASSWORD` environment variable is not set
- Shows a warning when using default credentials
- Suitable for local development only

**Production Mode:**
- **REQUIRES** `DB_PASSWORD` environment variable to be set
- No default passwords accepted
- All credentials must come from secure sources

#### Environment Variables Setup

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Set secure passwords:**
   ```bash
   # .env file
   DB_PASSWORD=your_very_secure_random_password_here
   ```

3. **Never commit `.env` to version control:**
   - The `.gitignore` file already excludes `.env` files
   - Use `.env.example` for documentation only

#### Security Best Practices

1. **Use Strong Passwords:**
   ```bash
   # Generate a secure password
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Enable SSL/TLS for Database Connections:**
   ```bash
   DB_URL="postgresql+psycopg2://user:pass@host:port/db?sslmode=require"
   ```

3. **Use Secrets Management in Production:**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - Google Cloud Secret Manager

4. **Regular Security Maintenance:**
   - Rotate credentials quarterly
   - Update dependencies regularly
   - Monitor access logs
   - Perform security audits

#### Configuration Validation

The application will show warnings if running with insecure configuration:

```python
UserWarning: DB_PASSWORD not set! Using insecure default for development only.
Set DB_PASSWORD environment variable in production!
```

**Never ignore this warning in production environments.**

### Additional Security Resources

For comprehensive security guidance, see:
- **[SECURITY.md](SECURITY.md)** - Detailed security documentation
- **[.env.example](.env.example)** - Example environment configuration
- [Temporal Security Best Practices](https://docs.temporal.io/security)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

### Reporting Security Issues

If you discover a security vulnerability, please email: [security-contact@example.com]

**Do not open public issues for security vulnerabilities.**

## License

[Your License Here]

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review logs in Temporal UI (http://localhost:8233)
- Consult `CLAUDE.md` for implementation details
