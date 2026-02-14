# 🎓 Sentinel Integration Tutorial

Sentinel is a **Python Package**, not a Java JAR. You install it using `pip`.

## 1. Installation

If you are building a Python application (FastAPI, Django, Flask, or a Script), run:

```bash
# In the future, this will be: pip install sentinel-sdk
# For now (Development Mode):
pip install -e ./sdk
```

## 2. Configuration

You need an **API Key** and an **Organization ID** (Tenant ID).
*   **API Key:** Defined in your Sentinel Server's `.env` file (Variable: `SECRET_KEY`).
*   **Org ID:** Just a string to identify your project (e.g., `billing-service`).

## 3. Usage Example

### Scenario: Logging a "User Deleted" Event

Paste this code where your delete logic happens:

```python
from sentinel_sdk import SentinelClient

# Initialize connection
client = SentinelClient(
    base_url="http://localhost:8000",
    api_key="change_me_to_random_string",  # Must match server SECRET_KEY
    org_id="billing-service"
)

def delete_user(user_id):
    # ... your delete logic ...
    
    # Send Audit Log
    success = client.log(
        actor="admin@company.com",
        action="delete_user",
        resource=user_id,
        context={"reason": "GDPR request", "ip": "1.2.3.4"}
    )
    
    if success:
        print("✅ Audited successfully")
    else:
        print("⚠️ Warning: Audit log failed (Sentinel might be down)")
```

## 4. How to Verify?

Go to your Sentinel Server database (or use the verification script) to see the cryptographic proof.
