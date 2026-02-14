from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.audit.service import log_event
from src.db.session import get_db
from src.core.auth_dependency import get_api_key

router = APIRouter()

@router.post("/log")
async def create_log(
    org_id: str,
    actor_id: str,
    action: str,
    resource: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_api_key) # <--- ADDED SECURITY
):
    """
    Securely triggers an audit log. Requires valid X-Sentinel-Key.
    """
    try:
        new_log = await log_event(db, org_id, actor_id, action, resource)
        return {"msg": "Log created", "log_id": str(new_log.id), "curr_hash": new_log.curr_hash}
    except Exception as e:
        # If service busy (concurrency), let the client know
        if "Audit Log Busy" in str(e):
             raise HTTPException(status_code=503, detail="Service Busy, please retry")
        raise HTTPException(status_code=500, detail=str(e))
