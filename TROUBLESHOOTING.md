# Troubleshooting Guide

Common issues and solutions for the Sentinel platform.

## 🚨 Critical Issues

### 1. "Race condition detected" (IntegrityError)
**Symptom:** API returns 503 "Service Busy".
**Cause:** Two requests tried to write to the audit log simultaneously with the same `prev_hash`. Sentinel's optimistic locking caught this to prevent a chain fork.
**Solution:**
-   **Immediate:** The client should retry the request with exponential backoff.
-   **Permanent:** If this happens frequently, increasing the `max_retries` in `src/audit/service.py` may help, but ultimately this indicates a need for an architectural change (Queue-based writing).

### 2. "BROKEN CHAIN at index X" (Verification Failure)
**Symptom:** Running `tests/verify_chain.py` prints `BROKEN CHAIN`.
**Cause:** The cryptographic link between logs is invalid. This usually means a manual DB edit happened, or a race condition was not correctly handled (Chain Forking).
**Solution:**
-   Identify the `org_id` and timestamp of the break.
-   Check DB logs for unauthorized deletes/updates.
-   **Note:** In a real production scenario, this indicates a security breach.

---

## 🛠️ Setup & Runtime Errors

### 3. `ModuleNotFoundError: No module named 'src'`
**Cause:** Running python scripts from the wrong directory.
**Solution:** Always run python commands from the **root** `sentinel/` folder.
-   ✅ `python tests/stress_test.py`
-   ❌ `cd tests && python stress_test.py`

### 4. Database Connection Refused
**Symptom:** `Connection refused` or `Is the server running on port 5432?`
**Solution:**
1.  Ensure Docker container is up: `docker ps` should show `sentinel_db`.
2.  Check `.env` `DATABASE_URL`. If running locally (not in Docker), `localhost` works. If running **inside** Docker, use `db` (the service name).

### 5. "Missing API Key" / 403 Forbidden
**Cause:** You are calling a protected endpoint without auth.
**Solution:**
-   Add header: `X-Sentinel-Key: change_this_secret_in_prod` (or whatever is in your `.env`).
-   Or verify you are hitting a public endpoint (`/health`, `/docs`).

---

## 🔍 Debugging Tools

### database inspection
Connect to the running DB to see raw data:
```bash
docker exec -it sentinel_db psql -U sentinel -d sentinel_prod
# inside psql:
select * from audit_logs order by timestamp desc limit 5;
```

### Resetting the World
If you need a completely clean slate (WARNING: DELETES ALL DATA):
```bash
docker-compose down -v
docker-compose up --build
```
