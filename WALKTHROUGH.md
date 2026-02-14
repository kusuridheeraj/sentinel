# 🛡️ Sentinel — Verification Walkthrough

> **Goal:** Verify the Zero-Trust Architecture and Immutable Logging.

---

## 1. Setup & Run

```bash
cd sentinel
# Create venv (optional but recommended)
python -m venv venv
./venv/Scripts/Activate

# Install deps
pip install -r requirements.txt

# Run the Server
uvicorn src.main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 2. Verify Authentication

**Action:**
Open browser to `http://127.0.0.1:8000/auth/login`

**Expected JSON:**
```json
{
  "msg": "Redirect user to this URL",
  "url": "https://login.microsoftonline.com/..."
}
```
*This confirms the OIDC Adapter is configured and ready to handshake with Azure AD.*

---

## 3. Verify Immutable Hash Chain

**Action:**
Check the code in `src/audit/service.py` or run a manual test (requires DB).

**Key Code to Show Interviewers:**
```python
# src/core/security.py

def calculate_log_hash(...):
    payload = f"{prev_hash}{timestamp}{actor}{action}..."
    return hashlib.sha256(payload.encode()).hexdigest()
```
*This 4-line function is the difference between a standard log and a blockchain.*

---

## 4. Verify ABAC Policy Engine

**Action:**
Check `src/policy/engine.py`.

**Key Logic:**
It doesn't just check roles. It checks `user.dept == resource.owner` and `time < 18:00`.
This proves "Zero Trust" thinking.

---

## 5. Next Steps

- Connect a real PostgreSQL DB.
- Run `alembic upgrade head` to create tables.
- Start logging real events!
