# Sentinel - Trade-offs & Analysis

## 1. Concurrency & Integrity Failure (Confirmed)
Our stress tests (`tests/stress_test.py`) combined with chain verification (`tests/verify_chain.py`) revealed a critical flaw in the current implementation.

### The Flaw: Chain Forking
When multiple requests hit `/audit/log` simultaneously:
1.  Request A reads the latest log (Hash X).
2.  Request B reads the latest log (Hash X).
3.  Request A inserts Log A with `prev_hash = X`.
4.  Request B inserts Log B with `prev_hash = X`.

Both logs are accepted because:
*   `curr_hash` is unique (Request A and B have different timestamps/actors, so their resulting hashes are different).
*   There is no unique constraint on `prev_hash` (nor should there be strictly, but logical application constraints are missing).

### Result
The audit log is not a linear chain but a tree with many forks. An attacker could hide a malicious action in a "orphan branch" that is valid but ignored by verifiers following the "main" chain.

### Fix
*   **Database Locking:** Use `SELECT ... FOR UPDATE` (Postgres) to lock the tip of the chain.
*   **Optimistic Concurrency:** Add a `version` column or unique constraint on `prev_hash` (if strictly linear).
*   **Queueing:** Push logs to a queue (Kafka/Redis) and have a single serial consumer write to the DB.

## 2. Database Choice
*   **Current:** SQLite (for testing) / Postgres (intended).
*   **Trade-off:** SQL databases are good for structured queries but Hash Chaining on every insert kills write throughput.
*   **Alternative:** Use an append-only ledger database like QLDB or specialized blockchain, but that adds vendor lock-in.

## 3. Synchronous Hashing
*   **Current:** Hashing happens in the request/response cycle.
*   **Impact:** Adds ~5-10ms latency per request.
*   **Justification:** Immediate consistency. We know the log is sealed before confirming the action.
