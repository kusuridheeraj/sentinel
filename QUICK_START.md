# Quick Start Guide: Sentinel

Get the Sentinel platform running in under 5 minutes.

## Prerequisites
-   **Docker & Docker Compose** (Recommended)
-   **Python 3.9+** (If running without Docker)
-   **Git**

---

## 🚀 Option 1: Docker (Fastest)

This spins up the API and a PostgreSQL database instantly.

### 1. Clone & Enter
```bash
git clone <repo-url> sentinel
cd sentinel
```

### 2. Configure Environment
```bash
cp .env.example .env
# No edits needed for local dev!
```

### 3. Launch
```bash
docker-compose up --build
```
*Wait for `Uvicorn running on http://0.0.0.0:8000`*

### 4. Verify
Open http://localhost:8000/docs in your browser.
You should see the Swagger UI.

---

## 🐍 Option 2: Local Python (For Debugging)

If you want to run the code directly on your machine.

### 1. Setup Database (Docker)
We still need a DB. Local setup assumes a Postgres instance or fallback to SQLite.
```bash
docker-compose up -d db
```

### 2. Install Dependencies
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run App
```bash
uvicorn src.main:app --reload
```

---

## ✅ Sanity Check

Run this `curl` command to ensure the system is live:
```bash
curl http://localhost:8000/health
# Response: {"status":"ok","service":"sentinel"}
```

## 🛑 Stop Everything
```bash
docker-compose down
```
