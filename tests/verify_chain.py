import asyncio
from sqlalchemy.future import select
from sqlalchemy import asc
from src.db.session import AsyncSessionLocal
from src.db.models import AuditLog

async def verify_chain():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AuditLog).order_by(asc(AuditLog.timestamp)))
        logs = result.scalars().all()
        
    print(f"Verifying {len(logs)} logs...")
    
    broken = False
    for i in range(1, len(logs)):
        prev = logs[i-1]
        curr = logs[i]
        
        if curr.prev_hash != prev.curr_hash:
            print(f"BROKEN CHAIN at index {i}!")
            print(f"Log {curr.id} prev_hash: {curr.prev_hash}")
            print(f"Log {prev.id} curr_hash: {prev.curr_hash}")
            broken = True
            break
            
    if not broken:
        print("Chain is VALID.")

if __name__ == "__main__":
    asyncio.run(verify_chain())
