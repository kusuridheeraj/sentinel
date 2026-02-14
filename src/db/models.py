from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(String, index=True, nullable=False)  # Tenant Isolation
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    actor_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    context = Column(JSON, nullable=True)  # IP, User-Agent, etc.
    
    # The Blockchain Links
    prev_hash = Column(String(64), nullable=False)
    curr_hash = Column(String(64), nullable=False, unique=True)

    def __repr__(self):
        return f"<AuditLog {self.id} | {self.action} | {self.curr_hash[:8]}...>"
