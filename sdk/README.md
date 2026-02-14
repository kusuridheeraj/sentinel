# Sentinel Python SDK

The official Python client for the Sentinel Immutable Audit Log platform.

## Installation

```bash
pip install sentinel-sdk
```

## Usage

### Synchronous (Scripts)
```python
from sentinel_sdk import SentinelClient

client = SentinelClient(
    base_url="http://localhost:8000",
    api_key="secret",
    org_id="my-company"
)

# This will not crash your app if Sentinel is down (fail_silent=True)
client.log(
    actor="alice@admin.com",
    action="delete_user",
    resource="user_123"
)
```

### Asynchronous (FastAPI/Django)
```python
@app.post("/users/{id}")
async def delete_user(id: str):
    await db.delete(id)
    
    # Fire and forget (mostly)
    await client.alog(
        actor="bob@admin.com", 
        action="delete", 
        resource=id
    )
```
