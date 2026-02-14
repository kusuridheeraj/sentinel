from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from src.db.models import AuditLog
from src.core.security import calculate_log_hash
from datetime import datetime, timezone

async def log_event(
    session: AsyncSession,
    org_id: str,
    actor_id: str,
    action: str,
    resource: str,
    context: dict = None
) -> AuditLog:
    """
    Logs an event with cryptographic linkage (Hash Chain).
    MUST be called within a transaction to ensure no gaps.
    """
    # 1. Get the latest log for this Org (Locking strategy needed in high concurrency)
    # For MVP: We assume serializable isolation or low concurrency.
    # In Prod: explicit row locking or optimistic concurrency control.
    
    result = await session.execute(
        select(AuditLog)
        .filter(AuditLog.org_id == org_id)
        .order_by(desc(AuditLog.timestamp))
        .limit(1)
    )
    last_log = result.scalars().first()

    # 2. Determine Previous Hash
    if last_log:
        prev_hash = last_log.curr_hash
    else:
        # Genesis Block for this Tenant
        prev_hash = "0" * 64

    # 3. Calculate Current Hash
    now = datetime.now(timezone.utc)
    curr_hash = calculate_log_hash(prev_hash, now, actor_id, action, resource, context)

    # 4. Create & Insert
    new_log = AuditLog(
        org_id=org_id,
        timestamp=now,
        actor_id=actor_id,
        action=action,
        resource=resource,
        context=context,
        prev_hash=prev_hash,
        curr_hash=curr_hash
    )
    
    session.add(new_log)
    await session.commit()
    await session.refresh(new_log)
    
    return new_log
