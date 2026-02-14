from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import get_settings
from src.auth import router as auth_router
from src.audit import router as audit_router
from src.db.models import Base
from src.db.session import engine

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Zero-Trust Access Gateway with Immutable Audit Logging",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Security: Strict CORS
# In production, specific origins only.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(audit_router.router, prefix="/audit", tags=["Audit"])

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health_check():
    """
    K8s/Docker health probe.
    Returns 200 if the service is up.
    Does NOT guarantee DB connectivity (separate probe).
    """
    return {"status": "ok", "service": "sentinel"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
