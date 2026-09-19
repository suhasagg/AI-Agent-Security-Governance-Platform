from fastapi import FastAPI,Depends,Header,HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter,make_asgi_app
from agents import InputGuardrailTripwireTriggered,OutputGuardrailTripwireTriggered
from .config import settings
from .database import init_db,get_db
from .contracts import AgentRequest,PolicyRequest,ApprovalRequest
from .security import authenticate,scan_text,redact
from .policy import evaluate
from .approvals import ApprovalStore
from .audit import append
from .rate_limit import check
from .agent_runtime import run_agent
from .telemetry import tracer

app=FastAPI(title="AI Agent Security & Governance Platform",version="1.0.0")
app.mount("/metrics",make_asgi_app())
redis=Redis.from_url(settings.redis_url,decode_responses=True)
approvals=ApprovalStore(redis)
DECISIONS=Counter("agent_governance_decisions_total","Governance decisions",["effect","risk"])

@app.on_event("startup")
async def startup():await init_db()

def ident(header):
    try:return authenticate(header)
    except PermissionError as e:raise HTTPException(401,str(e))

@app.get("/health")
async def health():return {"status":"ok"}

@app.post("/v1/policy/evaluate")
async def policy(req:PolicyRequest,authorization:str|None=Header(None),
                 db:AsyncSession=Depends(get_db)):
    identity=ident(authorization)
    d=evaluate(identity,req.tool,req.arguments)
    DECISIONS.labels(d.effect,d.risk).inc()
    await append(db,identity,"policy_evaluation",d.effect,
      {"tool":req.tool,"risk":d.risk,"reason":d.reason})
    return d

@app.post("/v1/approvals")
async def approve(req:ApprovalRequest,authorization:str|None=Header(None),
                  db:AsyncSession=Depends(get_db)):
    identity=ident(authorization)
    if "admin" not in identity.roles:raise HTTPException(403,"admin role required to approve")
    d=evaluate(identity,req.tool,req.arguments)
    if d.effect!="approval":raise HTTPException(400,"action does not require approval")
    token=await approvals.issue(identity,req.tool,req.arguments,req.ttl_seconds)
    await append(db,identity,"approval_issued","allow",{"tool":req.tool,"risk":d.risk})
    return {"approval_token":token,"expires_in":req.ttl_seconds}

@app.post("/v1/agent/run")
async def agent(req:AgentRequest,authorization:str|None=Header(None),
                db:AsyncSession=Depends(get_db)):
    identity=ident(authorization)
    try:await check(redis,identity.tenant_id,identity.subject)
    except RuntimeError as e:raise HTTPException(429,str(e))
    scan=scan_text(req.message)
    if scan["secret"] or scan["prompt_injection"]:
        await append(db,identity,"agent_input","deny",scan)
        raise HTTPException(400,"input blocked by security policy")
    try:
        with tracer.start_as_current_span("governed.agent.run") as span:
            span.set_attribute("tenant.id",identity.tenant_id)
            span.set_attribute("principal.id",identity.subject)
            result=await run_agent(identity,req.message)
        safe=redact(result)
        await append(db,identity,"agent_run","allow",{"input_scan":scan,"output_length":len(safe)})
        return {"answer":safe,"governance":{"input_scan":scan}}
    except (InputGuardrailTripwireTriggered,OutputGuardrailTripwireTriggered):
        await append(db,identity,"agent_guardrail","deny",{"reason":"guardrail tripwire"})
        raise HTTPException(400,"agent execution blocked by guardrail")
