# Sentinel Codebase Guide

This document provides a comprehensive deep-dive into the Sentinel codebase, a Zero-Trust Access & Audit Platform. It is designed to help new developers understand the architecture, core logic, and operational details of the system.

---

## 1. PROJECT OVERVIEW & ARCHITECTURE

### High-Level Architecture
- **Type**: Monolithic API (Modular Monolith)
- **Purpose**: A B2B SaaS platform providing Zero-Trust Access Control (ABAC) with Cryptographically Immutable Audit Logs. It acts as a secure gateway that validates user identity and context before granting access, while maintaining a tamper-proof audit trail.
- **Tech Stack**:
    -   **Language**: Python 3.9+
    -   **Framework**: FastAPI (Async Web Framework)
    -   **Database**: PostgreSQL (Primary Data Store) with `asyncpg` driver.
    -   **ORM**: SQLAlchemy (Async)
    -   **Migrations**: Alembic
    -   **Containerization**: Docker & Docker Compose

### Architecture Diagram
```ascii
[Client Apps / Users]
       |
       v
  [Load Balancer] (Nginx/Cloud - Not in repo)
       |
       v
+-----------------------+
|  SENTINEL API (FastAPI)|
|                       |
|  [Auth Middleware]    |<----(OIDC)---- [Azure AD / Okta]
|  (JWT / API Key)      |
|                       |
|  [Policy Engine]      | (ABAC Evaluation)
|                       |
|  [Audit Service]      | (Hash Chaining)
+----------+------------+
           |
    (Async SQL)
           v
+-----------------------+
|  PostgreSQL Database  |
|                       |
|  [Audit Logs Table]   |
|  [Policies Table]     |
+-----------------------+
```

### Technology Trade-offs
| Choice | Why Chosen | Alternatives | Trade-offs | when to Switch |
| :--- | :--- | :--- | :--- | :--- |
| **FastAPI** | High performance (async), auto-docs (Swagger), type safety (Pydantic). | Flask, Django | Steeper learning curve for async; younger ecosystem than Django. | If building a traditional server-rendered MVC app (use Django). |
| **PostgreSQL** | Robustness, JSONB support (for flexible contexts), widely understood. | MongoDB, DynamoDB | Relational schema enforcement can be rigid (mitigated by JSONB). | If data is massive & unstructured (Petabytes) and relational integrity is less critical. |
| **SQLAlchemy (Async)** | Powerful ORM, DB-agnostic, excellent migration tool (Alembic). | Tortoise ORM, SQLModel | Complex API compared to simpler ORMs. | If the app is extremely simple (CRUD only), SQLModel might be cleaner. |
| **Hash Chaining (In-DB)** | Simple, immutable log verification without external blockchain complexity. | Blockchain (Eth/Hyperledger) | Centralized trust (DB admin *could* rewrite chain, though detectable). | If decentralized, public trust is required (use Public Blockchain). |

---

## 2. PROJECT STRUCTURE DEEP DIVE

### Directory Structure
```
/sentinel
├── /src
│   ├── /audit           # Immutable Audit Log Logic
│   │   ├── router.py    # API Endpoints
│   │   └── service.py   # Core Logic (Hash Chaining)
│   ├── /auth            # Authentication Module
│   │   └── router.py    # OIDC / Login Endpoints
│   ├── /core            # Core Configuration & Utilities
│   │   ├── config.py    # Env Vars & Settings
│   │   ├── security.py  # Hashing Algos
│   │   └── auth_dependency.py # Dependency Injection
│   ├── /db              # Database Layer
│   │   ├── models.py    # SQLAlchemy Models
│   │   └── session.py   # DB Connection Session
│   ├── /policy          # ABAC Policy Engine
│   │   └── engine.py    # Policy Evaluation Logic
│   └── main.py          # App Entrypoint
├── /tests               # Test Scripts
└── docker-compose.yml   # Local Dev Infrastructure
```

### Module Responsibilities

#### `src/audit`
-   **Purpose**: Handles the creation and retrieval of immutable audit logs.
-   **Key Files**: `service.py` (Implements the hash chain logic and optimistic concurrency control).
-   **Dependencies**: Depends on `src/db` (for storage) and `src/core` (for hashing).

#### `src/auth`
-   **Purpose**: Manages user authentication via OIDC (Azure AD) and API Key validation.
-   **Key Files**: `router.py` (Login flows), `auth_dependency.py` (Protects routes).
-   **Entry Points**: `/auth/login`, `/auth/callback`.

#### `src/policy`
-   **Purpose**: Executes access decisions based on attributes (User, Resource, Environment).
-   **Key Files**: `engine.py` (Contains the `evaluate` method).
-   **Usage**: Called by other services/middleware to check permissions.

#### `src/db`
-   **Purpose**: Centralizes database connection and model definitions.
-   **Key Files**: `models.py` (Defines `AuditLog` table), `session.py` (Async engine setup).

---

## 3. CORE FUNCTIONALITY BREAKDOWN

### Feature: Immutable Audit Logging
**What it does**: Records every action (who, what, where) in a tamper-evident chain.
**Why it exists**: To prove compliance and detect if logs have been altered.
**How it works**:
1.  Fetch the latest log for the organization.
2.  Compute `SHA256(prev_hash + timestamp + details)`.
3.  Insert new log with this hash.
**Code location**: `src/audit/service.py` -> `log_event`.
**Dependencies**: PostgreSQL (for atomic commits).
**Edge cases**: High concurrency (race conditions on `prev_hash`) is handled via retries/optimistic locking.

### Feature: ABAC Policy Engine
**What it does**: Decides if a user can access a resource.
**How it works**: Compares a JSON Policy against a Request Context.
**Code location**: `src/policy/engine.py` -> `PolicyEngine.evaluate`.
**Example**: User dept "Sales" matches Policy user.dept "Sales" -> ALLOW.

---

## 4. DATA FLOW DOCUMENTATION

### Request/Response Flow (Audit Log Example)

1.  **Entry Point**: `POST /audit/log` (`src/audit/router.py`)
2.  **Validation**: `Pydantic` validates input types. `auth_dependency` checks `X-Sentinel-Key`.
3.  **Business Logic**: `log_event` (`src/audit/service.py`) calculates the hash.
    -   *Logic*: Reads last hash -> Calculates new hash -> Tries to insert.
4.  **Data Access**: `session.add()` -> `session.commit()` (`SQLAlchemy`).
5.  **Error Handling**: If `IntegrityError` (race condition), rollback and retry.
6.  **Response**: Returns JSON with `log_id` and `curr_hash`.

### Database Schema
-   **Table**: `audit_logs`
-   **Columns**:
    -   `id`: UUID
    -   `org_id`: Tenant Identifier
    -   `prev_hash`: Link to parent
    -   `curr_hash`: Cryptographic identity of this node
    -   `timestamp`, `actor_id`, `action`, `resource`, `context` (JSONB)
-   **Constraint**: Unique constraint on `(org_id, prev_hash)` prevents "forking" the chain.

---

## 5. SETUP & RUNNING GUIDE

### Prerequisites
-   Docker & Docker Compose
-   Python 3.9+ (if running locally without Docker)

### Installation Steps
```bash
# 1. Clone the repo
git clone <repo-url>
cd sentinel

# 2. Create local environment file
cp .env.example .env
# Edit .env to add your keys (or stick with defaults for dev)
```

### Running the Application

**Using Docker (Recommended)**
```bash
# Starts API and DB
docker-compose up --build
```

**Running Locally**
```bash
# 1. Start DB
docker-compose up -d db

# 2. Install dependencies
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. Run App
uvicorn src.main:app --reload
```

---

## 6. TESTING GUIDE

### Test Structure
-   `tests/stress_test.py`: Concurrency test. Spawns N async requests to ensure the hash chain doesn't break under load.
-   `tests/verify_chain.py`: Utility script to traverse the DB and verify cryptographic integrity.

### Running Tests
```bash
# Run Stress Test (Requires app running on localhost:8000)
python tests/stress_test.py

# Verify Chain Integrity (Connects to DB directly)
python tests/verify_chain.py
```

### Writing New Tests
-   Use `pytest` for unit tests (currently missing in repo, should be added).
-   Mock `AsyncSession` when testing service logic in isolation.

---

## 7. COMMON DEVELOPMENT SCENARIOS

### Adding a New API Endpoint
1.  **Create Router**: Add new functions in `src/<module>/router.py`.
2.  **Define Schema**: Use `Pydantic` models for request/response bodies.
3.  **Register Router**: Import and `app.include_router(...)` in `src/main.py`.

### Debugging Issues
-   **Race Conditions**: Check logs for "Race condition detected". Increase `max_retries` in `src/audit/service.py` if frequent.
-   **Database Locks**: Ensure `session.commit()` is awaited.

---

## 8. DEPENDENCIES
-   **fastapi**: Web framework.
-   **uvicorn**: ASGI Server.
-   **sqlalchemy**: Database ORM.
-   **alembic**: DB Migrations.
-   **asyncpg**: Async PostgreSQL driver.
-   **python-jose**: JWT handling.

---

## 9. SECURITY & BEST PRACTICES
-   **Authentication**: Uses OIDC (Azure AD) for users and API Keys for services.
-   **Input Validation**: Strict validation via Pydantic.
-   **Integrity**: Hash chaining prevents log tampering.
-   **Tenancy**: All queries MUST filter by `org_id`.

---

## 10. PERFORMANCE CONSIDERATIONS
-   **Database Indexing**: `org_id` and `timestamp` are indexed.
-   **Async I/O**: All DB and Network calls are async to handle high throughput.
-   **Bottleneck**: Hash calculation is CPU bound (lightweight), but DB locking on the "head" of the chain is the main contention point.

---

## 11. ERROR HANDLING & RECOVERY
-   **Optimistic Concurrency**: `src/audit/service.py` catches `IntegrityError` and retries.
-   **Global Handlers**: `FastAPI` default exception handlers for 422/500.

---

## 12. DEPLOYMENT & DEVOPS
-   **Docker**: Primary deployment artifact.
-   **Env Vars**: `DATABASE_URL`, `SECRET_KEY`, `AZURE_*` must be set in production.
-   **Health Check**: `/health` endpoint available.

---

## 13. REAL-WORLD PROBLEM-SOLVING GUIDE

**How do I add a new field to the Audit Log?**
1.  Modify `AuditLog` in `src/db/models.py`.
2.  Run `alembic revision --autogenerate` (if configured) or manually update DB.
3.  Update `calculate_log_hash` in `src/core/security.py` to include the new field in the hash.
4.  Update behaviors in `src/audit/service.py`.

**How do I rotate the API Key?**
1.  Change `SECRET_KEY` env var.
2.  Restart the service.

---

## 14. CODE PATTERNS & CONVENTIONS
-   **Dependency Injection**: Use `Depends(...)` for DB sessions and Auth.
-   **Async/Await**: Used everywhere. Do not use blocking calls.
-   **Structure**: Router -> Service -> DB.

---

## 15. CRITICAL "IF REMOVED" ANALYSIS

**"What breaks if I remove..."**
-   **Hash Calculation (`security.py`)**: The "Immutable" promise is broken. Logs become just plain text rows.
-   **Unique Constraint (`models.py`)**: You lose protection against forking/branching the history.
-   **Retry Loop (`service.py`)**: High concurrency requests will fail with 500 Errors instead of successfully completing.
