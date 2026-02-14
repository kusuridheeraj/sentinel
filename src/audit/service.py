from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from src.db.models import AuditLog
from src.core.security import calculate_log_hash
from datetime import datetime, timezone
import asyncio
import logging

# Setup Logger
logger = logging.getLogger("sentinel.audit")

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
    Uses Optimistic Concurrency Control (Retry on race condition).
    """
    max_retries = 5
    attempt = 0
    
    while attempt < max_retries:
        attempt += 1
        try:
            # 1. Get the latest log for this Org
            # We start a NEW transaction scope for each attempt if using a DB that requires it.
            # In SQLAlchemy async session, we just proceed.
            
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
            
        except IntegrityError:
            # Race Condition detected!
            # Another request inserted a log with the same prev_hash before we did.
            await session.rollback()
            # print(f"Race condition detected (Attempt {attempt}). Retrying...")
            if attempt >= max_retries:
                logger.error("Failed to log event after max retries due to high concurrency.")
                raise Exception("Audit Log Busy: Please try again.")
            
            # Small jitter backoff to prevent thundering herd
            await asyncio.sleep(0.01 * attempt)
            
    return None
