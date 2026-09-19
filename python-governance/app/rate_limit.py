import time
from redis.asyncio import Redis
async def check(r:Redis,tenant,subject,limit=60):
    key=f"rate:{tenant}:{subject}:{int(time.time()//60)}"
    n=await r.incr(key)
    if n==1:await r.expire(key,70)
    if n>limit:raise RuntimeError("rate limit exceeded")
