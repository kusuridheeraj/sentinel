from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, index=True, nullable=False)  # Tenant Isolation
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    actor_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    context = Column(JSON, nullable=True)
    
    # The Blockchain Links
    prev_hash = Column(String(64), nullable=False)
    curr_hash = Column(String(64), nullable=False, unique=True)

    # CRITICAL SECURITY FIX: Prevent Forking Attacks
    # Ensure that for a given Org, only ONE log can point to a specific previous hash.
    __table_args__ = (
        UniqueConstraint('org_id', 'prev_hash', name='uq_org_prev_hash'),
    )

    def __repr__(self):
        return f"<AuditLog {self.id} | {self.action} | {self.curr_hash[:8]}...>"
