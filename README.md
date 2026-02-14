# 🛡️ SENTINEL — Zero-Trust Access & Audit Platform

> **A B2B SaaS platform for Zero-Trust Access Control (ABAC) with Cryptographically Immutable Audit Logs.**

---

## 🚀 The Mission

Enterprises fail security audits not because they lack firewalls, but because they **lose track of who did what**.
Sentinel is a **Fail-Closed, Zero-Trust Gateway** that ensures:
1.  **Access is Context-Aware:** Not just "Who are you?", but "Where are you? What time is it? Is your device safe?" (ABAC).
2.  **History is Immutable:** Audit logs are linked via cryptographic hash chains. If a hacker deletes a log, the chain breaks.
3.  **Multi-Tenant by Design:** Built for B2B, enforcing strict data isolation.

---

## 🏗 Architecture

- **Core:** Python (FastAPI)
- **Identity:** OIDC Adapter (Azure AD / Okta)
- **Policy Engine:** ABAC logic with Redis caching
- **Storage:** PostgreSQL (Hot Data) + S3 (Archival)
- **Integrity:** SHA-256 Hash Chaining (Mini-Blockchain)

---

## 📚 Documentation

- [Architecture & Design Decisions](docs/ARCHITECTURE.md)
- [Immutable Logs & Debugging Guide](docs/IMMUTABLE_LOGS.md)
- [Codebase Guide (Deep Dive)](CODEBASE_GUIDE.md)
- [Quick Start Guide](QUICK_START.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Architecture Decisions (ADR)](ARCHITECTURE_DECISIONS.md)
- [New Developer Guide](NEW_DEVELOPER_GUIDE.md)

---

## 🛠 Roadmap

- [ ] **Architecture:** Architecture & Threat Model (✅ Done)
- [ ] **Auth:** Auth Flow & OIDC Integration
- [ ] **Audit:** Immutable Audit Engine (Hash Chains)
- [ ] **Policy:** Policy Engine (ABAC)
- [ ] **Detection:** Anomaly Detection
- [ ] **Hardening:** Security Hardening (Vault)
- [ ] **Polish:** Final Polish & Blog

---

## License
MIT
