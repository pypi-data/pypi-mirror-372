# Tiny Queue

A modular, extensible Python queue service with support for FIFO, priority, async, and persistent queues. Designed for production use in enterprise applications with monitoring, decorators, and retry logic.

---

## 🚀 Features

- ✅ FIFO, Priority, Async, and Persistent Queues
- 🔒 Thread-safe and async-compatible
- 💾 File-based persistence
- 📊 Monitoring hooks (logging, metrics)
- 🔁 Retry and rate-limiting utilities
- 🧩 Decorators for queuing function calls
- 🧪 Easy to test and extend

---

## 📦 Installation

```bash
pip install tiny-queue
```
Or clone the repo for local development:

```bash
git clone https://github.com/js-sravan/tiny-queue.git
cd queue-service
pip install -e .
```

## Usage

### FIFO Queue

```python
from queue_service import FIFOQueue

q = FIFOQueue()
q.enqueue("task1")
print(q.dequeue())  # → "task1"
```

### Priority Queue
```python
from queue_service import PriorityQueue

pq = PriorityQueue()
pq.enqueue("urgent", priority=1)
pq.enqueue("low", priority=5)
print(pq.dequeue())  # → "urgent"
```

### Async Queue
```python
import asyncio
from queue_service import AsyncQueue

async def main():
    aq = AsyncQueue()
    await aq.enqueue("async-task")
    task = await aq.dequeue()
    print(task)

asyncio.run(main())
```

### Persistent Queue
```python
from queue_service import PersistentQueue

pq = PersistentQueue(filepath="my_queue.json")
pq.enqueue("saved-task")
print(pq.dequeue())
```

## Additional Utilities

### Retry Decorator
```python
from queue_service import retry

@retry(times=3, delay=2)
def fragile_task():
    # May fail intermittently
    pass
```

### Rate Limiting
```python
from queue_service import rate_limit

@rate_limit(calls_per_second=5)
def api_call():
    pass
```

### Queueing Functions
```python
from queue_service import FIFOQueue, queue_task

q = FIFOQueue()

@queue_task(q)
def process_data(x):
    return x * 2

process_data(10)  # Enqueued as a task
```