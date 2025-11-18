# Search Attributes & Advanced Workflow Querying

This document explains the search attributes feature that enables querying and filtering workflows by customer information, order totals, and priority levels.

## Overview

Search attributes are indexed fields that allow you to find workflows using custom criteria. This implementation adds:

- **Customer Management**: Separate customer table with name, email, phone
- **Order Metadata**: Order totals and priority levels stored with workflows
- **Search Capabilities**: Query workflows by customer, amount, priority, and more

## New Database Schema

### Customers Table
```sql
customers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Enhanced Orders Table
```sql
orders (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,  -- NEW: Foreign key to customers
    order_total DECIMAL(10, 2),  -- NEW: Order amount
    priority TEXT,  -- NEW: NORMAL, HIGH, URGENT
    state TEXT NOT NULL,
    address_json TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

## Search Attributes

Four search attributes are registered with Temporal:

1. **CustomerId** (Keyword): Exact customer ID matching
2. **CustomerName** (Text): Full-text search on customer names
3. **OrderTotal** (Double): Numeric range queries on order amounts
4. **Priority** (Keyword): Filter by NORMAL, HIGH, or URGENT

## Setup Instructions

### 1. Reset Database (if upgrading from old schema)

The new schema adds foreign key constraints, so you need to recreate the database:

```bash
# Stop services
docker-compose down

# Remove old database volume
docker volume rm temporal-order-orchestrator_postgres_data

# Start services (will recreate database with new schema)
docker-compose up -d

# Wait ~30 seconds for services to initialize
```

### 2. Register Search Attributes

Choose one method:

**Option A: Using the batch/shell script (recommended)**

Windows:
```bash
scripts\setup_search_attributes.bat
```

macOS/Linux:
```bash
chmod +x scripts/setup_search_attributes.sh
./scripts/setup_search_attributes.sh
```

**Option B: Using Python script**
```bash
python -m scripts.setup_search_attributes
```

**Option C: Manual registration using tctl**
```bash
docker exec temporal tctl admin cluster add-search-attributes --name CustomerId --type Keyword
docker exec temporal tctl admin cluster add-search-attributes --name CustomerName --type Text
docker exec temporal tctl admin cluster add-search-attributes --name OrderTotal --type Double
docker exec temporal tctl admin cluster add-search-attributes --name Priority --type Keyword
```

## Usage Examples

### API Examples

#### 1. Create a Customer
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
  "id": "cust-a1b2c3d4",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "555-0123",
  "created_at": "2025-01-15 10:30:00"
}
```

#### 2. Start an Order with Customer Info
```bash
curl -X POST http://localhost:8000/orders/order-001/start \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust-a1b2c3d4",
    "order_total": 250.50,
    "priority": "HIGH"
  }'
```

#### 3. Search Workflows

**Find all orders for a customer:**
```bash
curl "http://localhost:8000/orders?customer_id=cust-a1b2c3d4"
```

**Find high-priority orders:**
```bash
curl "http://localhost:8000/orders?priority=HIGH"
```

**Find orders between $100-$500:**
```bash
curl "http://localhost:8000/orders?min_total=100&max_total=500"
```

**Combined search:**
```bash
curl "http://localhost:8000/orders?customer_id=cust-a1b2c3d4&priority=URGENT&min_total=1000"
```

### CLI Examples

#### 1. Start Order (generates customer automatically)
```bash
python -m scripts.cli start
```

#### 2. Start Order with Customer Details
```bash
python -m scripts.cli start order-001 payment-001 cust-001 "Jane Smith" 350.75 HIGH
```

Parameters:
- `order-001`: Order ID
- `payment-001`: Payment ID
- `cust-001`: Customer ID
- `"Jane Smith"`: Customer name
- `350.75`: Order total
- `HIGH`: Priority (NORMAL, HIGH, URGENT)

### Temporal UI

1. Open http://localhost:8080
2. Go to "Workflows"
3. Click "Add Filter"
4. Select search attribute and enter criteria:
   - `CustomerId = "cust-12345"`
   - `Priority = "HIGH"`
   - `OrderTotal >= 100`

## Query Syntax

When using the API or Temporal UI, you can build complex queries:

### Exact Match (Keyword fields)
```
CustomerId = "cust-12345"
Priority = "URGENT"
```

### Text Search
```
CustomerName = "John"
```

### Numeric Range
```
OrderTotal >= 100
OrderTotal <= 500
OrderTotal >= 100 AND OrderTotal <= 500
```

### Combined Queries
```
CustomerId = "cust-12345" AND Priority = "HIGH"
Priority = "URGENT" AND OrderTotal >= 1000
CustomerName = "Smith" AND OrderTotal >= 100
```

## API Endpoints

### Customer Management

- `POST /customers` - Create a new customer
- `GET /customers/{customer_id}` - Get customer by ID
- `GET /customers` - List all customers

### Order Workflows

- `POST /orders/{order_id}/start` - Start workflow (now requires customer_id)
- `GET /orders` - List/search workflows with filters
- `GET /orders/{order_id}/status` - Get workflow status
- `GET /orders/{order_id}/result` - Get workflow result

### Search Parameters

The `GET /orders` endpoint accepts:
- `customer_id` - Filter by exact customer ID
- `customer_name` - Search by customer name
- `priority` - Filter by priority (NORMAL, HIGH, URGENT)
- `min_total` - Minimum order amount
- `max_total` - Maximum order amount
- `limit` - Max results (default: 50)

## Code Changes Summary

### Workflow Changes
- `OrderWorkflow.run()` now accepts: `customer_id`, `customer_name`, `order_total`, `priority`
- Search attributes are set using `workflow.upsert_search_attributes()`

### Activity Changes
- `receive_order_activity()` now accepts customer and order metadata

### Function Changes
- `order_received()` creates order with customer reference
- `payment_charged()` uses `order_total` from order dict

## Troubleshooting

### Search returns no results

1. Verify search attributes are registered:
```bash
docker exec temporal tctl admin cluster get-search-attributes
```

2. Check if CustomerId, CustomerName, OrderTotal, and Priority are listed

### Foreign key constraint error

This means you're trying to create an order with a non-existent customer_id:

1. Create the customer first using `POST /customers`
2. Use the returned `customer_id` when starting the workflow

### "Search attribute not found" error

Run the setup script:
```bash
scripts\setup_search_attributes.bat  # Windows
./scripts/setup_search_attributes.sh  # macOS/Linux
```

## Performance Considerations

- Search attributes are indexed, providing fast query performance
- Keyword fields (CustomerId, Priority) support exact matching only
- Text fields (CustomerName) support full-text search but may be slower
- Numeric fields (OrderTotal) support range queries efficiently

## Next Steps

With search attributes in place, you can now:

1. **Build dashboards** showing orders by customer, priority, or value
2. **Create reports** on order volumes and totals
3. **Implement alerts** for high-value or high-priority orders
4. **Enable customer portals** where users can see their order history
5. **Add more attributes** like order status, region, or product category

## Additional Resources

- [Temporal Search Attributes Documentation](https://docs.temporal.io/visibility)
- [Temporal Query Syntax](https://docs.temporal.io/visibility#list-filter)
- API docs available at: http://localhost:8000/docs
