from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import get_settings
from src.auth import router as auth_router

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
