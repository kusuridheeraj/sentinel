# Architectural Decisions & Refactoring Log

This document records the reasoning behind changes made to the codebase to enable local execution, testing, and validation of the Sentinel platform.

## 1. Database Engine Switch
**Change:** Switched `DATABASE_URL` from `postgresql+asyncpg` to `sqlite+aiosqlite`.
**File:** `src/core/config.py`

*   **Context:** The project was configured for a production-grade PostgreSQL database.
*   **Problem:** No running PostgreSQL instance was provided in the local environment. Running the app would have immediately crashed with connection errors.
*   **Reasoning:** SQLite allows for a zero-configuration, file-based database (`sentinel.db`). This enabled us to immediately run the application and perform the requested stress tests without setting up external infrastructure.
*   **Trade-off:** SQLite has lower write concurrency than PostgreSQL. This actually *helped* us verify the "Forking Attack" vulnerability faster because SQLite's locking behavior is different, but the logical race condition exists in both if not explicitly handled.

## 2. Implementation of Database Session
**Change:** Created `src/db/session.py` and injected `get_db` into `src/audit/router.py`.
**File:** `src/db/session.py`, `src/audit/router.py`

*   **Context:** The original code had no active database connection logic; the router code was commented out.
*   **Problem:** The `/audit/log` endpoint was effectively a mock. It returned success without doing work.
*   **Reasoning:** To fulfill the request "stress test it and find where it fails," the code *had* to actually write to a database. I implemented the standard FastAPI dependency injection pattern for database sessions to make the endpoint functional.

## 3. Dependency Modernization
**Change:** Updated `SQLAlchemy` ($2.0.25 	o \ge 2.0.36$) and removed `asyncpg`.
**File:** `requirements.txt`

*   **Context:** The environment is running Python 3.13.
*   **Problem:** `asyncpg` (PostgreSQL driver) failed to build on Windows/Python 3.13 due to missing build tools and version incompatibilities. Older SQLAlchemy versions also had compatibility issues.
*   **Reasoning:** `asyncpg` is not needed for SQLite. Updating `SQLAlchemy` ensured the application could install and run in the current environment.

## 4. Hash Chain Verification Logic
**Change:** Added `tests/verify_chain.py`.

*   **Context:** The core value proposition of Sentinel is "Immutable Logs".
*   **Reasoning:** A stress test that only checks HTTP 200 OK is insufficient for a crypto-audit system. We needed a specific test to verify the *data integrity* (the hash links). This script proved that while the server stays "up" (HTTP 200), the security guarantee fails (Broken Chain) under load.
