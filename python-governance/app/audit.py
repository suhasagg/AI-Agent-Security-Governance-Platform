import hashlib,json,uuid
from sqlalchemy import select
from .models import AuditEvent
async def append(db,identity,event_type,decision,details):
    q=select(AuditEvent).where(AuditEvent.tenant_id==identity.tenant_id).order_by(AuditEvent.created_at.desc()).limit(1)
    prev=(await db.scalar(q))
    previous=prev.event_hash if prev else "0"*64
    safe=json.dumps(details,sort_keys=True,separators=(",",":"),default=str)
    event_id="evt-"+uuid.uuid4().hex[:16]
    h=hashlib.sha256((previous+"|"+event_id+"|"+identity.tenant_id+"|"+identity.subject+"|"+event_type+"|"+decision+"|"+safe).encode()).hexdigest()
    db.add(AuditEvent(id=event_id,tenant_id=identity.tenant_id,subject=identity.subject,
      event_type=event_type,decision=decision,details=safe,previous_hash=previous,event_hash=h))
    await db.commit()
    return event_id
