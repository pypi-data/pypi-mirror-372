# Worker Component Development Guide

This guide covers arq worker architecture patterns and development for the Aegis Stack worker component.

## Worker Architecture (arq)

Aegis Stack uses pure **arq patterns** without custom wrappers, following native arq CLI and configuration patterns.

### Worker Configuration Structure

Each worker queue has its own `WorkerSettings` class:
- `app/components/worker/queues/system.py` - System maintenance worker
- `app/components/worker/queues/load_test.py` - Load testing worker  
- `app/components/worker/queues/media.py` - Media processing worker

### Worker Services in Docker

Workers run as separate Docker services with specific names:
- **`worker-system`** - System maintenance tasks (low concurrency, high reliability)
- **`worker-load-test`** - High-concurrency load testing (up to 50 concurrent jobs)
- **`worker-media`** - File/media processing (commented out by default)

## Adding Worker Tasks

### 1. Create Task Functions
Tasks are pure async functions in `app/components/worker/tasks/`:
```python
# app/components/worker/tasks/my_tasks.py
async def my_background_task() -> dict[str, str]:
    """My custom background task."""
    logger.info("Running my background task")
    
    # Your task logic here
    await asyncio.sleep(1)  # Simulate work
    
    return {
        "status": "completed",
        "timestamp": datetime.now(UTC).isoformat(),
        "task": "my_background_task"
    }
```

### 2. Register with Worker Queue
Import and add to the appropriate `WorkerSettings`:
```python
# app/components/worker/queues/system.py
from app.components.worker.tasks.my_tasks import my_background_task

class WorkerSettings:
    functions = [
        system_health_check,
        cleanup_temp_files,
        my_background_task,  # Add your task here
    ]
    
    # Standard arq configuration
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    queue_name = "arq:queue:system"
    max_jobs = 15
    job_timeout = 300
```

## Native arq CLI Usage

### Worker Health Checks
```bash
# Check if workers can connect to Redis and validate configuration
uv run python -m arq app.components.worker.queues.system.WorkerSettings --check
uv run python -m arq app.components.worker.queues.load_test.WorkerSettings --check
uv run python -m arq app.components.worker.queues.media.WorkerSettings --check
```

### Local Worker Development
```bash
# Run worker locally with auto-reload for development
uv run python -m arq app.components.worker.queues.system.WorkerSettings --watch app/

# Run worker in burst mode (process all jobs and exit)
uv run python -m arq app.components.worker.queues.system.WorkerSettings --burst
```

### Worker Configuration in Health Checks

The health system reads worker configuration from `app/core/config.py` but workers themselves use their own `WorkerSettings` classes:

```python
# Health system reads this for monitoring
WORKER_QUEUES: dict[str, dict[str, Any]] = {
    "system": {
        "description": "System maintenance and monitoring tasks",
        "max_jobs": 15,
        "timeout_seconds": 300,
        "queue_name": "arq:queue:system",
    },
    "load_test": {
        "description": "Load testing and performance testing",
        "max_jobs": 50,
        "timeout_seconds": 60,
        "queue_name": "arq:queue:load_test",
    }
}

# But workers use their own WorkerSettings classes for actual configuration
```

## Key Differences from Custom Worker Systems

### ✅ What We Do (Pure arq):
- Use native arq CLI: `python -m arq WorkerSettings`
- Standard `WorkerSettings` classes with `functions` list
- Direct task imports into worker configurations
- Native arq health checking and monitoring

### ❌ What We Don't Do (Avoided custom patterns):
- Custom worker wrapper classes
- Central worker registry systems
- Custom CLI commands for workers
- Configuration-driven task discovery

This approach keeps workers transparent and lets developers use arq exactly as documented in the official arq documentation.

## Docker Worker Debugging Commands

### View Worker Logs
```bash
# View specific worker logs
docker compose logs worker-system             # System worker logs
docker compose logs worker-load-test          # Load test worker logs
docker compose logs -f worker-system          # Follow system worker in real-time
docker compose logs -f worker-load-test       # Follow load test worker in real-time

# View all workers at once
docker compose logs -f worker-system worker-load-test

# Filter for errors in specific workers
docker compose logs worker-load-test | grep "ERROR\|failed\|TypeError"

# Monitor worker processes and resources
docker compose exec worker-system ps aux      # Check system worker processes
docker compose exec worker-load-test ps aux   # Check load test worker processes
docker stats worker-system worker-load-test   # Monitor resource usage
docker compose restart worker-system          # Restart specific worker
```

### Essential Docker Log Monitoring

**Check Worker Logs for Load Test Issues:**
```bash
# View real-time worker logs
docker compose logs -f worker

# Check specific container logs  
docker logs <container-id>

# View logs with timestamps
docker compose logs --timestamps worker

# Search logs for specific errors
docker compose logs worker | grep "TypeError\|failed"

# Check all service logs
docker compose logs -f
```

**Load Test Debugging Workflow:**
1. **Run Load Test**: `uv run full-stack load-test run --type io_simulation --tasks 10`
2. **Monitor Worker Logs**: `docker compose logs -f worker-load-test` (in separate terminal)
3. **Look for**: 
   - `TypeError` messages indicating parameter mismatches
   - Task completion vs failure counts (`j_complete=X j_failed=Y`)
   - Task execution times and errors
   - Redis connection issues

**Common Error Patterns:**
- `TypeError: function() got an unexpected keyword argument 'param'` - Parameter mismatch between orchestrator and task function
- `j_failed=X` increasing rapidly - Worker tasks failing due to code issues
- `Redis connection failed` - Infrastructure connectivity problems
- `delayed=X.XXs` - Queue saturation or worker overload

**System Health Verification:**
```bash
# Check all containers
docker compose ps

# Check system health via API
uv run full-stack health status --detailed

# Monitor Redis connection
docker compose logs redis
```

## Worker Development Best Practices

### Task Design Patterns
1. **Pure Functions** - Tasks should be self-contained with minimal dependencies
2. **Error Handling** - Always include try/catch with proper logging
3. **Return Values** - Return structured data for monitoring and debugging
4. **Timeouts** - Set appropriate timeouts for different task types
5. **Retry Logic** - Use arq's built-in retry mechanisms

### Queue Management
1. **Separate Concerns** - Use different queues for different types of work
2. **Concurrency Limits** - Set appropriate max_jobs for each queue type
3. **Priority Queues** - Use different queues for different priorities
4. **Dead Letter Queues** - Monitor failed jobs and implement recovery

### Monitoring and Observability
1. **Structured Logging** - Use structured logs for easy parsing
2. **Metrics Collection** - Track task execution times and success rates
3. **Health Checks** - Implement health checks for worker availability
4. **Alerting** - Set up alerts for queue depth and failure rates

This approach ensures workers are maintainable, debuggable, and follow established patterns.