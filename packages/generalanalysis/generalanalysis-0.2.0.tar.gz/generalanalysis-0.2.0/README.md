# General Analysis SDK

Python SDK for General Analysis AI Guardrails.

## Installation

```bash
pip install generalanalysis
```

## Quick Start

```python
import generalanalysis

# Uses GA_API_KEY env var by default
client = generalanalysis.Client()

# Check text against guard policies
result = client.guards.invoke(guard_id=1, text="Text to check")

if result.block:
    print("Blocked:", [p.name for p in result.policies if not p.passed])
```

## Configuration

```python
# API key priority: parameter > GA_API_KEY env var
client = generalanalysis.Client(api_key="your-key")

# Custom endpoint (default: https://redit-api-dev.generalanalysis.com)
client = generalanalysis.Client(base_url="http://localhost:5001")

# Resource cleanup
with generalanalysis.Client() as client:
    guards = client.guards.list()
```

## API Reference

### Guards Operations

```python
# List guards
guards = client.guards.list()

# Get guard details  
guard = client.guards.get(guard_id=1)

# Invoke guard
result = client.guards.invoke(guard_id=1, text="...")
print(f"Blocked: {result.block}, Latency: {result.latency_ms}ms")

# Generate policies from job
policies = client.guards.generate_policies_from_job(job_id=123)

# Get logs (paginated)
logs = client.guards.list_logs(guard_id=1, page=1, page_size=50)
```

## Async Support

```python
import asyncio
import generalanalysis

async def main():
    async with generalanalysis.AsyncClient() as client:
        results = await asyncio.gather(*[
            client.guards.invoke(guard_id=1, text=t) 
            for t in texts
        ])
```

## Error Handling

```python
from generalanalysis import AuthenticationError, GuardNotFoundError

try:
    result = client.guards.invoke(guard_id=999, text="test")
except GuardNotFoundError:
    print("Guard not found")
except AuthenticationError:
    print("Invalid API key")
```

## Type Hints

Fully typed for IDE support:

```python
from generalanalysis import Client, Guard, GuardInvokeResult

def check_safety(client: Client, text: str) -> bool:
    result: GuardInvokeResult = client.guards.invoke(guard_id=1, text=text)
    return not result.block
```

## License

MIT