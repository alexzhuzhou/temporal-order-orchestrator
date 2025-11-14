# Troubleshooting Guide

This guide covers common issues you may encounter when running the Temporal Order Orchestrator and their solutions.

## Table of Contents

- [Worker Issues](#worker-issues)
- [Database Issues](#database-issues)
- [Workflow Execution Issues](#workflow-execution-issues)
- [Temporal Server Issues](#temporal-server-issues)
- [Port Conflicts](#port-conflicts)
- [Development Issues](#development-issues)

## Worker Issues

### ModuleNotFoundError: No module named 'temporal_app'

**Error:**
```
ModuleNotFoundError: No module named 'temporal_app'
```

**Cause:** Running the worker script directly without using Python's module execution.

**Solution:**
```bash
# Correct way:
python -m temporal_app.worker_dev

# Incorrect way (don't do this):
python temporal_app/worker_dev.py
```

**Why:** Using `-m` tells Python to run the file as a module, which properly sets up the Python path.

---

### ImportError: attempted relative import with no known parent package

**Error:**
```
ImportError: attempted relative import with no known parent package
```

**Cause:** The worker script contains relative imports (`.config`, `.workflows`) but is being run as a standalone script.

**Solution:** Ensure imports in `worker_dev.py` are absolute:
```python
# Correct:
from temporal_app.config import TEMPORAL_HOST
from temporal_app.workflows import OrderWorkflow

# Incorrect:
from .config import TEMPORAL_HOST
from .workflows import OrderWorkflow
```

---

### Worker Connects But Shows No Activity

**Symptoms:** Worker starts without errors but workflows aren't being processed.

**Possible Causes:**

1. **Task queue mismatch:**
   - Check that the worker's task queue matches the workflow submission:
   ```python
   # In worker_dev.py
   TASK_QUEUE = "dev-tq"

   # In run_order_once.py
   task_queue=TASK_QUEUE  # Must match!
   ```

2. **Temporal server not running:**
   - Verify: Visit http://localhost:8233
   - Start it: `temporal server start-dev`

3. **Wrong Temporal namespace:**
   - Default is `"default"`
   - Check `temporal_app/config.py` and ensure it matches your server

---

## Database Issues

### Password Authentication Failed for User "trellis"

**Error:**
```
OperationalError: connection to server at "localhost", port 5432 failed:
FATAL: password authentication failed for user "trellis"
```

**Cause 1: Multiple PostgreSQL Instances**

Another PostgreSQL instance is running on port 5432 (often a system-installed PostgreSQL).

**Diagnosis:**
```bash
# Windows
netstat -ano | findstr :5432

# macOS/Linux
lsof -i :5432
```

If you see multiple processes, you have conflicting PostgreSQL instances.

**Solution:**

**Option A: Stop the conflicting PostgreSQL (Recommended)**

```bash
# Windows - Find the service name
sc query | findstr postgres

# Stop it
net stop postgresql-x64-17

# Disable auto-start
sc config postgresql-x64-17 start=disabled
```

```bash
# macOS
brew services stop postgresql@17

# Linux
sudo systemctl stop postgresql
sudo systemctl disable postgresql
```

**Option B: Change Docker's port**

Edit `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"  # Use 5433 on host, 5432 in container
```

Update `temporal_app/config.py`:
```python
DB_URL = os.getenv(
    "DB_URL",
    "postgresql+psycopg2://trellis:trellis@localhost:5433/trellis",
)
```

**Cause 2: Database Initialized with Different Credentials**

The Docker volume contains a database from a previous run with different credentials.

**Solution:**
```bash
# Stop and remove the database with volumes
docker-compose down -v

# Start fresh
docker-compose up -d

# Verify schema was created
docker logs temporal-order-orchestrator-db-1
# Should see: "CREATE TABLE orders", "CREATE TABLE payments", etc.
```

---

### Connection Refused to Database

**Error:**
```
psycopg2.OperationalError: connection to server at "localhost", port 5432 failed:
Connection refused
```

**Cause:** PostgreSQL container is not running.

**Solution:**
```bash
# Check if running
docker ps

# If not listed, start it
docker-compose up -d

# Check logs for errors
docker logs temporal-order-orchestrator-db-1
```

---

### Missing Tables (Table Does Not Exist)

**Error:**
```
relation "orders" does not exist
relation "payments" does not exist
```

**Cause:** Database schema was not initialized.

**Solution:**

**Option 1: Recreate database container**
```bash
docker-compose down -v
docker-compose up -d
```

**Option 2: Manual initialization**
```bash
python scripts/init_db.py
```

**Option 3: Execute schema manually**
```bash
docker exec -i temporal-order-orchestrator-db-1 psql -U trellis -d trellis < db/schema.sql
```

---

## Workflow Execution Issues

### TypeError: execute_activity() takes from 1 to 2 positional arguments

**Error:**
```
TypeError: execute_activity() takes from 1 to 2 positional arguments but 3 positional
arguments (and 2 keyword-only arguments) were given
```

**Cause:** Code was updated while old workflows are still running. Temporal replays workflows from their history, so they try to execute the old code signature.

**Solution:**

**Option 1: Start a new workflow (Recommended)**
```bash
# The script automatically generates unique IDs
python -m scripts.run_order_once
```

**Option 2: Terminate the old workflow**
```bash
# Via Temporal CLI
temporal workflow terminate --workflow-id <workflow-id>

# Or via UI: http://localhost:8233 → Select workflow → Terminate
```

**Prevention:** Ensure activity calls use `args`:
```python
# Correct:
await workflow.execute_activity(
    charge_payment_activity,
    args=[order, payment_id],
    **activity_opts(),
)

# Incorrect:
await workflow.execute_activity(
    charge_payment_activity,
    order,
    payment_id,
    **activity_opts(),
)
```

---

### Activity Timeout Errors

**Error:**
```
temporalio.exceptions.TimeoutError: activity ScheduleToClose timeout
```

**Cause:** This is **expected behavior** due to intentional flakiness. Activities have:
- 4-second timeout
- 33% chance of sleeping for 300 seconds
- 33% chance of immediate error
- 33% chance of success

**Solutions:**

**Option 1: Wait for retries**
Temporal will automatically retry. Check the Temporal UI to see retry attempts.

**Option 2: Disable flakiness temporarily**

Edit `temporal_app/functions.py`:
```python
async def flaky_call() -> None:
    """Either raise an error or sleep long enough to trigger an activity timeout."""
    return  # Always succeed immediately

    # Comment out the random logic:
    # rand_num = random.random()
    # if rand_num < 0.33:
    #     raise RuntimeError("Forced failure for testing")
    # if rand_num < 0.67:
    #     await asyncio.sleep(300)
```

**Remember to restart the worker after changes!**

**Option 3: Increase activity timeouts**

Edit `temporal_app/activities.py`:
```python
ACTIVITY_SCHEDULE_TO_CLOSE = timedelta(seconds=310)  # Longer than sleep
ACTIVITY_START_TO_CLOSE = timedelta(seconds=310)
```

---

### Workflow Timeout After 15 Seconds

**Error:**
```
Workflow execution failed: timeout
```

**Cause:** The workflow run timeout (15 seconds) is shorter than the time needed to complete with retries.

**Solution:**

Edit `scripts/run_order_once.py`:
```python
handle = await client.start_workflow(
    OrderWorkflow.run,
    args=[order_id, payment_id],
    id=order_id,
    task_queue=TASK_QUEUE,
    run_timeout=timedelta(seconds=300),  # Increase timeout
)
```

---

### TypeError: Expected value to be str, was <class 'list'>

**Error:**
```
TypeError: Expected value to be str, was <class 'list'>
```

**Cause:** Child workflow invocation issue with return type handling.

**Solution:** Use `execute_child_workflow` instead of `start_child_workflow`:

```python
# Correct:
shipping_result = await workflow.execute_child_workflow(
    ShippingWorkflow.run,
    args=[order],
)

# Incorrect:
shipping_handle = workflow.start_child_workflow(
    ShippingWorkflow.run,
    args=[order],
)
shipping_result = await shipping_handle
```

---

## Temporal Server Issues

### Connection Refused to Temporal Server

**Error:**
```
Error: failed to connect to Temporal server: connection refused
```

**Cause:** Temporal server is not running.

**Solution:**

**Option 1: Start with Temporal CLI**
```bash
temporal server start-dev
```

**Option 2: Start with Docker**
```bash
docker run -p 7233:7233 -p 8233:8233 temporalio/auto-setup:latest
```

**Verify it's running:**
- CLI: Check for output "Temporal server is running"
- Browser: Visit http://localhost:8233

---

### Temporal Web UI Not Loading

**Problem:** http://localhost:8233 shows "This site can't be reached"

**Cause 1: Server not started**
```bash
temporal server start-dev
```

**Cause 2: Wrong port**
- Web UI is on port 8233
- gRPC (worker) is on port 7233
- Ensure you're visiting http://localhost:8233 (with the 8)

**Cause 3: Port conflict**
```bash
# Check what's on port 8233
netstat -ano | findstr :8233  # Windows
lsof -i :8233                  # macOS/Linux
```

---

## Port Conflicts

### Port 5432 Already in Use

**Symptoms:** Database won't start, or docker-compose fails.

**Diagnosis:**
```bash
# Windows
netstat -ano | findstr :5432

# macOS/Linux
lsof -i :5432
```

**Solution:** See [Password Authentication Failed](#password-authentication-failed-for-user-trellis) → Multiple PostgreSQL Instances

---

### Port 7233 or 8233 Already in Use

**Symptoms:** Temporal server won't start.

**Solution:**

**Option 1: Stop conflicting service**
```bash
# Find the process
netstat -ano | findstr :7233  # Windows
lsof -i :7233                  # macOS/Linux

# Kill it
taskkill /PID <pid> /F        # Windows
kill -9 <pid>                  # macOS/Linux
```

**Option 2: Use different ports**

When starting Temporal with Docker:
```bash
docker run -p 7234:7233 -p 8234:8233 temporalio/auto-setup:latest
```

Update `temporal_app/config.py`:
```python
TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7234")
```

---

## Development Issues

### Changes Not Taking Effect

**Problem:** Code changes aren't reflected in workflow execution.

**Cause:** Worker wasn't restarted after code changes.

**Solution:**
1. Stop the worker (Ctrl+C)
2. Restart: `python -m temporal_app.worker_dev`

**Important:** Workflows currently executing will continue with old code. Start new workflows to use updated code.

---

### Bash Commands Show ".bashrc: line 10: cd" Error

**Error:**
```
/c/Users/Equipo/.bashrc: line 10: cd: /c/ALL PROGRAMMING PROJECS/Chevron-SQ:
No such file or directory
```

**Cause:** Your `.bashrc` tries to cd into a non-existent directory on every bash command.

**Solution:**
```bash
# Remove the problematic line
sed -i '10d' ~/.bashrc

# Verify it's gone
sed -n '8,12p' ~/.bashrc
```

This won't affect the current terminal session but will fix future bash commands.

---

### Virtual Environment Not Activating

**Problem:** `pip install` installs globally or shows permission errors.

**Solution:**

**Windows PowerShell:**
```powershell
# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate:
.venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Verify it's active:**
```bash
which python  # Should show path in .venv folder
```

---

### Database Shows Incorrect Data

**Problem:** Database has stale or test data from previous runs.

**Solution:**

**Option 1: Clear all data (keep schema)**
```bash
docker exec temporal-order-orchestrator-db-1 psql -U trellis -d trellis -c "
  TRUNCATE orders CASCADE;
  TRUNCATE payments CASCADE;
  TRUNCATE events CASCADE;
"
```

**Option 2: Fresh database**
```bash
docker-compose down -v
docker-compose up -d
```

---

## Getting Additional Help

If you're still experiencing issues:

1. **Check Temporal UI** (http://localhost:8233)
   - View workflow history
   - Check activity failures
   - Look for stack traces

2. **Check Worker Logs**
   - Look for exceptions in the terminal where worker is running

3. **Check Database Logs**
   ```bash
   docker logs temporal-order-orchestrator-db-1
   ```

4. **Check Temporal Server Logs**
   - Look at terminal where `temporal server start-dev` is running

5. **Enable Verbose Logging**

   Add to `worker_dev.py`:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

6. **Consult Documentation**
   - `README.md` - General setup and usage
   - `CLAUDE.md` - Detailed architecture documentation
   - [Temporal Docs](https://docs.temporal.io/) - Official documentation

---

## Common Gotchas

### 1. Forgetting to Restart the Worker

After changing any Python code, you **must** restart the worker for changes to take effect.

### 2. Port Conflicts from System Services

PostgreSQL and other database services often auto-start. Check `services.msc` (Windows) or `systemctl` (Linux) to disable unwanted auto-starts.

### 3. Using Relative Imports in Entry Scripts

Entry point scripts (`worker_dev.py`, `run_order_once.py`) should use absolute imports:
- ✅ `from temporal_app.config import TEMPORAL_HOST`
- ❌ `from .config import TEMPORAL_HOST`

### 4. Old Workflows Still Running

Temporal keeps workflows alive even if you restart the worker. Old workflows may fail if code changed. Start fresh workflows with new IDs.

### 5. Database Volume Persistence

Docker volumes persist between `docker-compose down` and `docker-compose up`. Use `-v` flag to remove volumes:
```bash
docker-compose down -v
```

### 6. Flakiness is Intentional

If workflows keep failing, remember that **67% failure rate is by design**. Either:
- Wait for eventual success (Temporal will retry)
- Disable flakiness temporarily
- Check Temporal UI to see retry patterns

---

## Quick Checklist

Before asking for help, verify:

- [ ] Virtual environment is activated
- [ ] All dependencies are installed (`pip install -r requirements.txt`)
- [ ] PostgreSQL is running (`docker ps`)
- [ ] No port conflicts (5432, 7233, 8233)
- [ ] Temporal server is running (visit http://localhost:8233)
- [ ] Worker is running (`python -m temporal_app.worker_dev`)
- [ ] Using correct import syntax (absolute, not relative)
- [ ] Worker was restarted after code changes
- [ ] Starting new workflows after code changes
- [ ] Database schema is initialized

---

## Need More Help?

- Review the main [README.md](README.md)
- Check [CLAUDE.md](CLAUDE.md) for architecture details
- Visit [Temporal Community](https://community.temporal.io/)
- Check [Temporal GitHub Issues](https://github.com/temporalio/sdk-python/issues)
