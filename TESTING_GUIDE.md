# Backend Testing Guide - Search Attributes

This guide walks through testing all the new search attributes functionality.

## Prerequisites Checklist

Before starting, ensure:
- [ ] Docker Desktop is running
- [ ] Python virtual environment is activated
- [ ] Dependencies are installed (`pip install -r requirements.txt`)

## Step 1: Reset Database & Start Services

Since the database schema changed, we need a fresh start:

```bash
# Stop everything
docker-compose down

# Remove old database volume (if it exists)
docker volume rm temporal-order-orchestrator_postgres_data

# Start services
docker-compose up -d

# Wait 30 seconds for services to initialize
```

**Verify services are running:**
```bash
docker-compose ps
```

You should see:
- ✅ `order-db` (healthy)
- ✅ `temporal-db` (healthy)
- ✅ `temporal` (healthy)
- ✅ `temporal-ui` (running)

## Step 2: Register Search Attributes

Run the setup script:

**Windows:**
```bash
scripts\setup_search_attributes.bat
```

**macOS/Linux:**
```bash
chmod +x scripts/setup_search_attributes.sh
./scripts/setup_search_attributes.sh
```

**Expected output:**
```
Adding CustomerId (Keyword)...
Adding CustomerName (Text)...
Adding OrderTotal (Double)...
Adding Priority (Keyword)...
✓ Search attributes setup complete!
```

**Verify registration:**
```bash
docker exec temporal tctl admin cluster get-search-attributes
```

Look for: `CustomerId`, `CustomerName`, `OrderTotal`, `Priority` in the output.

## Step 3: Start Workers

In a **new terminal** (with venv activated):

```bash
python -m temporal_app.worker_dev
```

**Expected output:**
```
Starting workers...
  Order Worker on: order-tq
  Shipping Worker on: shipping-tq
Workers started successfully
```

Keep this terminal running.

## Step 4: Start API Server

In **another new terminal** (with venv activated):

```bash
python -m api.server
```

**Expected output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Keep this terminal running.

## Step 5: Test Customer Management

Open a **new terminal** for testing.

### 5.1 Create Customers

```bash
# Create customer 1
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Alice Johnson\", \"email\": \"alice@example.com\", \"phone\": \"555-0101\"}"
```

**Expected response:**
```json
{
  "id": "cust-xxxxxxxx",
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "555-0101",
  "created_at": "2025-01-15 10:00:00"
}
```

**Save the customer ID!** You'll need it for the next steps.

```bash
# Create customer 2
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Bob Smith\", \"email\": \"bob@example.com\", \"phone\": \"555-0102\"}"
```

```bash
# Create customer 3
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Carol Davis\", \"email\": \"carol@example.com\", \"phone\": \"555-0103\"}"
```

### 5.2 List All Customers

```bash
curl http://localhost:8000/customers
```

**Expected:** JSON array with 3 customers.

### 5.3 Get Specific Customer

Replace `cust-xxxxxxxx` with actual customer ID:

```bash
curl http://localhost:8000/customers/cust-xxxxxxxx
```

## Step 6: Test Workflow Creation with Search Attributes

Replace `cust-xxxxxxxx` with Alice's customer ID from Step 5.1:

### 6.1 Create Order 1 (Alice, HIGH priority, $250)

```bash
curl -X POST http://localhost:8000/orders/order-001/start \
  -H "Content-Type: application/json" \
  -d "{\"customer_id\": \"cust-xxxxxxxx\", \"order_total\": 250.50, \"priority\": \"HIGH\"}"
```

**Expected response:**
```json
{
  "order_id": "order-001",
  "payment_id": "payment-xxxxxxxx",
  "customer_id": "cust-xxxxxxxx",
  "workflow_id": "order-001",
  "run_id": "...",
  "message": "Order workflow started successfully. Waiting for manual approval."
}
```

### 6.2 Create Order 2 (Bob, NORMAL priority, $150)

```bash
curl -X POST http://localhost:8000/orders/order-002/start \
  -H "Content-Type: application/json" \
  -d "{\"customer_id\": \"<bob-customer-id>\", \"order_total\": 150.00, \"priority\": \"NORMAL\"}"
```

### 6.3 Create Order 3 (Carol, URGENT priority, $750)

```bash
curl -X POST http://localhost:8000/orders/order-003/start \
  -H "Content-Type: application/json" \
  -d "{\"customer_id\": \"<carol-customer-id>\", \"order_total\": 750.00, \"priority\": \"URGENT\"}"
```

### 6.4 Create Order 4 (Alice, URGENT priority, $500)

```bash
curl -X POST http://localhost:8000/orders/order-004/start \
  -H "Content-Type: application/json" \
  -d "{\"customer_id\": \"<alice-customer-id>\", \"order_total\": 500.00, \"priority\": \"URGENT\"}"
```

**Check worker terminal** - you should see:
```
OrderWorkflow: Started for order_id=order-001, customer_id=cust-xxx...
OrderWorkflow: State transition to RECEIVING
OrderWorkflow: State transition to VALIDATING
OrderWorkflow: State transition to AWAITING_MANUAL_APPROVAL
```

## Step 7: Test Search Functionality

Now we'll test searching workflows by various criteria.

### 7.1 List All Orders

```bash
curl "http://localhost:8000/orders"
```

**Expected:** JSON with 4 workflows showing customer info, priority, totals.

### 7.2 Search by Customer ID (Alice's orders)

```bash
curl "http://localhost:8000/orders?customer_id=<alice-customer-id>"
```

**Expected:** 2 workflows (order-001 and order-004).

### 7.3 Search by Priority (URGENT only)

```bash
curl "http://localhost:8000/orders?priority=URGENT"
```

**Expected:** 2 workflows (order-003 and order-004).

### 7.4 Search by Order Total Range ($200-$600)

```bash
curl "http://localhost:8000/orders?min_total=200&max_total=600"
```

**Expected:** 2 workflows (order-001: $250.50 and order-004: $500).

### 7.5 Search by Customer Name

```bash
curl "http://localhost:8000/orders?customer_name=Alice"
```

**Expected:** 2 workflows (Alice's orders).

### 7.6 Combined Search (URGENT orders over $400)

```bash
curl "http://localhost:8000/orders?priority=URGENT&min_total=400"
```

**Expected:** 2 workflows (order-003: $750 and order-004: $500).

## Step 8: Test in Temporal UI

1. Open browser: http://localhost:8080
2. Click **"Workflows"** in left sidebar
3. You should see 4 running workflows

### 8.1 View Search Attributes

Click on any workflow → Look for **"Search Attributes"** section:
- CustomerId: `cust-xxxxxxxx`
- CustomerName: `Alice Johnson`
- OrderTotal: `250.5`
- Priority: `HIGH`

### 8.2 Filter in UI

1. Click **"Add a Filter"** button
2. Select **"CustomerId"** from dropdown
3. Enter: `cust-<alice-id>`
4. Click Apply

**Expected:** Only Alice's 2 workflows shown.

### 8.3 Advanced Query

1. Click "Advanced" (top right)
2. Enter query:
   ```
   Priority = "URGENT" AND OrderTotal >= 500
   ```
3. Press Enter

**Expected:** Shows order-003 and order-004.

## Step 9: Test CLI with Customer Info

Let's test the CLI with full customer details:

```bash
python -m scripts.cli start order-005 payment-005 cust-999 "David Lee" 425.00 HIGH
```

**Expected output:**
```
✓ Created customer: cust-999 (David Lee)

🚀 Starting OrderWorkflow
   Order ID: order-005
   Payment ID: payment-005
   Customer ID: cust-999
   Customer Name: David Lee
   Order Total: $425.00
   Priority: HIGH
   Task Queue: order-tq

✓ Workflow started!
```

**Verify in API:**
```bash
curl "http://localhost:8000/orders?customer_id=cust-999"
```

## Step 10: Test Complete Workflow Flow

Let's run one order through to completion:

### 10.1 Start Order
```bash
curl -X POST http://localhost:8000/orders/order-test/start \
  -H "Content-Type: application/json" \
  -d "{\"customer_id\": \"<any-customer-id>\", \"order_total\": 199.99, \"priority\": \"NORMAL\"}"
```

### 10.2 Check Status
```bash
curl http://localhost:8000/orders/order-test/status
```

**Expected:** `"workflow_state": "AWAITING_MANUAL_APPROVAL"`

### 10.3 Approve Order
```bash
curl -X POST http://localhost:8000/orders/order-test/signals/approve
```

### 10.4 Wait for Completion
```bash
curl http://localhost:8000/orders/order-test/result
```

**Expected:** Workflow completes successfully (may take a few seconds).

### 10.5 Verify in Database

```bash
docker exec -it order-db psql -U trellis -d trellis -c "SELECT * FROM orders WHERE id = 'order-test';"
```

**Expected:** Order record with SHIPPED state, customer_id, order_total, priority.

## Step 11: Verify Database Integrity

```bash
# Check customers
docker exec -it order-db psql -U trellis -d trellis -c "SELECT id, name, email FROM customers;"

# Check orders with customer info
docker exec -it order-db psql -U trellis -d trellis -c "
SELECT o.id, c.name as customer, o.state, o.order_total, o.priority
FROM orders o
JOIN customers c ON o.customer_id = c.id
ORDER BY o.created_at;"

# Check payments
docker exec -it order-db psql -U trellis -d trellis -c "SELECT order_id, status, amount FROM payments;"
```

## Troubleshooting

### Search Attributes Not Working

**Symptom:** API returns empty results or error about attributes.

**Fix:**
```bash
# Verify search attributes are registered
docker exec temporal tctl admin cluster get-search-attributes

# If missing, run setup again
scripts\setup_search_attributes.bat  # Windows
./scripts/setup_search_attributes.sh  # macOS/Linux
```

### Foreign Key Error

**Symptom:** Error: `foreign key constraint fails` when creating order.

**Fix:** Customer ID doesn't exist. Create customer first:
```bash
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Test User\", \"email\": \"test@example.com\"}"
```

### Workers Not Processing

**Symptom:** Workflows stuck in RECEIVING state.

**Fix:**
1. Check worker terminal is running
2. Restart workers: `python -m temporal_app.worker_dev`

### Search Returns No Results

**Symptom:** `GET /orders` returns empty even though workflows exist.

**Possible causes:**
1. Search attributes not registered (run setup script)
2. Workflows started before attributes were registered (restart workflows)
3. Wait ~10 seconds for Temporal to index new workflows

## Success Criteria

✅ All services running healthy
✅ Search attributes registered
✅ Customers created successfully
✅ Orders started with customer info
✅ Search by customer ID works
✅ Search by priority works
✅ Search by order total works
✅ Search by customer name works
✅ Combined searches work
✅ Temporal UI shows search attributes
✅ Database shows proper foreign key relationships

## Next Steps

Once all tests pass:
1. Create more complex queries
2. Test with larger datasets
3. Build frontend UI for search functionality
4. Add more search attributes (region, status, etc.)
5. Implement saved searches/filters
