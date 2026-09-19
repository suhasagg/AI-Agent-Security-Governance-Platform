from datetime import datetime
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,Text,DateTime
from .database import Base
class AuditEvent(Base):
    __tablename__="audit_events"
    id:Mapped[str]=mapped_column(String(80),primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(100),index=True)
    subject:Mapped[str]=mapped_column(String(100))
    event_type:Mapped[str]=mapped_column(String(80))
    decision:Mapped[str]=mapped_column(String(40))
    details:Mapped[str]=mapped_column(Text)
    previous_hash:Mapped[str]=mapped_column(String(64))
    event_hash:Mapped[str]=mapped_column(String(64),unique=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
