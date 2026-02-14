# New Developer Guide

Welcome to the Sentinel team! This guide outlines the first 10 tasks you should complete to become productive in this codebase.

## 🏁 Phase 1: Exploration (Day 1)

### 1. Run the "Happy Path"
-   Follow `QUICK_START.md` to get the app running.
-   Hit the `/health` endpoint.
-   **Goal:** Verify your environment is correct.

### 2. Read the "Bible"
-   Read `CODEBASE_GUIDE.md` top to bottom.
-   **Goal:** Understand the "Why" before the "How".

### 3. Explore the Database
-   Run the app via Docker.
-   Connect to the DB: `docker exec -it sentinel_db psql -U sentinel -d sentinel_prod`.
-   **Goal:** See the `audit_logs` schema and the `prev_hash`/`curr_hash` columns.

## 🛠️ Phase 2: Tinkering (Day 2)

### 4. Break the Chain
-   Manually "hack" the database: `UPDATE audit_logs SET action='malicious' WHERE id='<some-id>';`
-   Run `python tests/verify_chain.py`.
-   **Goal:** See the verification script scream "BROKEN CHAIN". Understand strictly *why* it broke.

### 5. Run the Stress Test
-   Run `python tests/stress_test.py` against a local instance.
-   **Goal:** Observe the `IntegrityError` / "Service Busy" logs. This is our biggest bottleneck.

### 6. Add a Logging Attribute
-   Modify `src/db/models.py` to add a `user_agent` column to `AuditLog`.
-   Update `src/core/security.py` to include it in the hash.
-   **Goal:** Understand the "Models -> Hash -> DB" dependency flow.

## 🚀 Phase 3: Contribution (Day 3-4)

### 7. Write a Policy
-   Modify `src/policy/engine.py` or extend the mock policy in `main.py`.
-   Try to create a rule that only allows access if `resource.sensitivity == 'low'`.
-   **Goal:** Get hands-on with the ABAC engine.

### 8. Create a Unit Test
-   Create `tests/test_policy.py`.
-   Write a test case for your new policy rule.
-   **Goal:** Learn the testing patterns (or lack thereof—we need more!).

### 9. Fix a "Bug"
-   (Simulated) The `/auth/login` endpoint is just a mock.
-   Challenge: Change the mock token return to include a `role: admin` claim.
-   **Goal:** Understand how the Auth module passes data to the rest of the app.

### 10. Open a PR
-   Push your `user_agent` change (Task 6) or your new test (Task 8) to a branch.
-   **Goal:** Get familiar with our Code Review standards.

---

## 🆘 Getting Help
-   **Docs:** Check `TROUBLESHOOTING.md` first.
-   **Logs:** `docker logs sentinel_api -f` is your best friend.
-   **Team:** Ping us in #sentinel-dev.
