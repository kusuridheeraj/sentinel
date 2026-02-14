# SENTINEL — Architecture & Design Document

> **Status:** Draft
> **Pattern:** Zero-Trust / Event Sourcing / ABAC
> **Focus:** B2B Multi-Tenant SaaS

---

## 1. Problem Statement (The "Why")

In B2B SaaS, "who accessed what" is usually an afterthought—a simple text log in a database.
**The Problem:**
1.  **Logs are mutable:** A rogue admin can delete their tracks from a standard SQL table.
2.  **RBAC is brittle:** "Admin" access is too broad. Real security needs context (Location, Time, Device).
3.  **Silent Failures:** If the audit logger fails, access often continues ("Fail Open"), leaving gaps.

**Sentinel's Solution:** A standalone, zero-trust access gateway that:
- Enforces **ABAC** (Context-aware access).
- Writes **Cryptographically Immutable Logs** (Tamper-evident).
- Fails **Closed** (No log = No access).

---

## 2. High-Level Architecture

We are building a **Multi-Tenant SaaS**. Data is isolated logically by `org_id`.

```mermaid
graph TD
    User[Client / User] -->|1. Request Access| Gateway[Sentinel Gateway API]
    
    subgraph "Sentinel Core (Zero Trust)"
        Gateway -->|2. Authenticate| IdP[Identity Provider Adapter]
        IdP -->|Azure AD / Mock| Azure[Azure AD]
        
        Gateway -->|3. Evaluate Policy| PolicyEngine[ABAC Policy Engine]
        PolicyEngine -->|Read Rules| Redis[Redis (Hot Config)]
        
        Gateway -->|4. Log Attempt| Audit[Immutable Audit Engine]
        Audit -->|Write Hash Chain| DB[(PostgreSQL)]
        Audit -->|Archive| S3[S3 (Cold Storage)]
    end
    
    subgraph "Admin & Ops"
        Admin -->|Configure| API[Management API]
        Ops -->|Monitor| Grafana[Grafana]
    end
```

### Components
1.  **Gateway API (FastAPI):** The entry point. Intercepts requests, validates tokens, enforces policy.
2.  **Policy Engine (ABAC):** Decides `ALLOW` or `DENY` based on attributes (User, Resource, Environment).
3.  **Audit Engine:** Calculates SHA-256 hashes of logs, links them to the previous entry, and writes to DB.
4.  **IdP Adapter:** Standardized interface for Identity Providers (initially Azure AD).

---

## 3. The "Zero-Trust" ABAC Model

We move beyond Roles (RBAC) to Attributes (ABAC).

**The Formula:**
`Decision = f(User_Attributes, Resource_Attributes, Environment_Conditions)`

### Defined Attributes
| Category | Attribute | Example |
| :--- | :--- | :--- |
| **User** | `role` | "finance_manager" |
| | `clearance_level` | 3 |
| | `mfa_enabled` | true |
| **Resource** | `type` | "payroll_report" |
| | `sensitivity` | "confidential" |
| | `owner_org` | "org_123" |
| **Environment** | `ip_country` | "US" |
| | `time_of_day` | "09:00" |
| | `device_trust` | "managed" |

### Example Policy (JSON)
```json
{
  "policy_id": "finance_access_01",
  "description": "Only Finance team can view payroll during work hours from US",
  "effect": "ALLOW",
  "rules": {
    "user.department": "finance",
    "resource.type": "payroll",
    "env.ip_country": "US",
    "env.time_hour": { "$gte": 9, "$lte": 17 }
  }
}
```

---

## 4. Threat Model (STRIDE)

We assume the network is hostile and the database administrator might be malicious.

| Threat | Definition | Sentinel Defense |
| :--- | :--- | :--- |
| **Spoofing** | Pretending to be another user | Strict OIDC Validation + MFA checks in attributes. |
| **Tampering** | Modifying audit logs to hide tracks | **Hash Chaining**: Each log contains `hash(prev_log + current_data)`. Modifying row N breaks row N+1. |
| **Repudiation** | "I didn't do that" | Signed logs (HMAC) + immutable ledger. |
| **Information Disclosure** | Leaking sensitive logs | Tenant isolation (`org_id` WHERE clauses) + S3 encryption. |
| **Denial of Service** | Flooding the audit engine | Async buffering (Redis Stream) + Rate Limiting (from Blackbox knowledge). |
| **Elevation of Privilege** | User changing their own role | Policy Engine checks `user.roles` from signed JWT only (not user input). |

---

## 5. Data Model & Tenant Isolation

**Strategy:** Row-Level Security (RLS) concept implemented in application logic.
Every table **MUST** have `org_id`.

### `audit_logs` Table
| Column | Type | Purpose |
| :--- | :--- | :--- |
| `id` | UUID | Unique ID |
| `org_id` | UUID | **Tenant Isolation** |
| `timestamp` | ISO8601 | When it happened |
| `actor_id` | String | Who did it |
| `action` | String | What they did |
| `resource` | String | Target resource |
| `context` | JSONB | Full request context (IP, headers) |
| `prev_hash` | String | **The Link:** Hash of the previous row |
| `curr_hash` | String | **The Seal:** SHA256(`prev_hash` + data) |

---

## 6. Failure Scenarios & Self-Healing

| Scenario | Behavior |
| :--- | :--- |
| **Redis (Cache) Down** | Policy Engine falls back to Postgres (slower, safe). |
| **Postgres (Write) Down** | **Fail Closed.** If we cannot log, we cannot allow access. (Security > Availability). |
| **Tampered Log Detected** | Background verifier flags the broken chain immediately. |
| **Azure AD Down** | Cached JWKS allow validation of existing tokens; new logins fail. |

---

## 7. Trade-offs (Staff Level)

1.  **Latency vs. Security:**
    *   *Trade-off:* We calculate SHA-256 hashes on the critical path of every write.
    *   *Justification:* For an *audit* system, integrity is the product. We accept <5ms overhead.

2.  **Fail-Closed vs. Availability:**
    *   *Trade-off:* If the DB is full, no one can login.
    *   *Justification:* A security system that fails open is a vulnerability. We choose safety.

3.  **ABAC Complexity:**
    *   *Trade-off:* Writing ABAC policies is harder than assigning roles.
    *   *Justification:* B2B Enterprise customers demand this granularity (e.g., GDPR, HIPAA compliance).

---

## 8. Next Steps (Implementation)

1.  **Auth Flow:** Set up FastAPI + Azure AD Mock.
2.  **Audit Engine:** Implement the `AuditLog` model with Hash Chaining.
3.  **Policy Engine:** Build the Policy Engine.
