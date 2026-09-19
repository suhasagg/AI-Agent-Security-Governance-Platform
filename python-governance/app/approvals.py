import hashlib,json,secrets,time
from redis.asyncio import Redis
def digest(tool,args):
    raw=json.dumps({"tool":tool,"arguments":args},sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()
class ApprovalStore:
    def __init__(self,r:Redis):self.r=r
    async def issue(self,identity,tool,args,ttl):
        token=secrets.token_urlsafe(32);h=hashlib.sha256(token.encode()).hexdigest()
        value={"subject":identity.subject,"tenant":identity.tenant_id,"digest":digest(tool,args),
               "expires":int(time.time())+ttl}
        await self.r.setex("approval:"+h,ttl,json.dumps(value))
        return token
    async def consume(self,token,identity,tool,args):
        h=hashlib.sha256(token.encode()).hexdigest();key="approval:"+h
        raw=await self.r.get(key)
        if not raw:return False
        data=json.loads(raw)
        ok=(data["tenant"]==identity.tenant_id and data["digest"]==digest(tool,args)
            and data["expires"]>=int(time.time()))
        if ok:await self.r.delete(key)
        return ok
