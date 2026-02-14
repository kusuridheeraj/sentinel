# Architecture Decision Records (ADR)

This document tracks significant architectural decisions made during the development of Sentinel, including the context, decision, and consequences.

## ADR-001: Monolithic Architecture

**Status:** Accepted
**Date:** 2024-01-01

**Context:**
We are building a B2B SaaS platform that needs tight integration between Authentication, Policy Evaluation, and Audit Logging. The team size is small.

**Decision:**
Build Sentinel as a **Modular Monolith** using FastAPI.

**Consequences:**
-   (+) Simplifies deployment (single Docker container).
-   (+) Shared database transactions for atomic operations across modules.
-   (+) No network latency between Policy Engine and Audit Service.
-   (-) Scaling individual components (e.g., just the Audit Engine) is harder than microservices.

## ADR-002: Immutable Audit Logs via Hash Chaining

**Status:** Accepted
**Date:** 2024-01-10

**Context:**
A core value proposition is "tamper-evident" logs.

**Decision:**
Implement a cryptographic hash chain within the relational database (`audit_logs` table). Each row stores `curr_hash = SHA256(prev_hash + row_data)`.

**Consequences:**
-   (+) Provides strong integrity guarantees without external blockchains.
-   (-) Introduces strict serialization on writes (concurrency bottleneck).
-   (-) "Forking" attacks are possible if not strictly enforced by unique constraints/locking.

## ADR-003: Database Engine (PostgreSQL vs SQLite)

**Status:** Accepted (with caveats for local dev)
**Date:** 2024-02-14

**Context:**
Production requires robust concurrency (PostgreSQL), but local development and CI ease is critical.

**Decision:**
-   **Production:** Use **PostgreSQL** for row-level locking and JSONB support.
-   **Local/Testing:** Support **SQLite** (via `aiosqlite`) for zero-setup execution.

**Consequences:**
-   (+) Developers can run tests immediately without Docker.
-   (-) Subtle behavior differences in locking between SQLite/Postgres can hide race conditions during local testing.

## ADR-004: Optimistic Concurrency Control

**Status:** Accepted
**Date:** 2024-02-14

**Context:**
Strict serialization of the hash chain causes significant contention under load. Locking the whole table kills performance.

**Decision:**
Use **Optimistic Concurrency** (`prev_hash` check) with a retry loop in the application layer.

**Consequences:**
-   (+) High read throughput.
-   (-) Write throughput suffers under heavy contention from the same Organization.
-   (-) Clients may experience 503 "Service Busy" during bursts and must retry.

## ADR-005: ABAC over RBAC

**Status:** Accepted
**Date:** 2024-01-15

**Context:**
Enterprise customers need granular permissions (e.g., "Only access payroll from the office between 9-5"). RBAC (Role-Based Access Control) is too coarse.

**Decision:**
Implement **Attribute-Based Access Control (ABAC)** where policies are JSON documents evaluated dynamically.

**Consequences:**
-   (+) Extremely flexible expressiveness.
-   (-) Higher complexity for admins to write policies.
-   (-) Policy evaluation is more compute-intensive than simple role checks.
