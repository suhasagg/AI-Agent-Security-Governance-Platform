import re
from .contracts import Identity
TOKENS={
 "demo-reader-token":Identity(subject="alice",tenant_id="acme",roles=["reader"]),
 "demo-operator-token":Identity(subject="bob",tenant_id="acme",roles=["reader","operator"]),
 "demo-admin-token":Identity(subject="carol",tenant_id="acme",roles=["reader","operator","admin"]),
 "globex-reader-token":Identity(subject="dave",tenant_id="globex",roles=["reader"]),
}
SECRET_PATTERNS=[
 re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
 re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
 re.compile(r"(?i)password\s*[:=]\s*\S+"),
]
PII_PATTERNS=[
 re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
 re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I),
]
INJECTION_MARKERS=[
 "ignore previous instructions","reveal system prompt","developer message",
 "bypass policy","disable guardrail","exfiltrate secrets",
]
def authenticate(header:str|None)->Identity:
    if not header or not header.startswith("Bearer "):raise PermissionError("missing bearer token")
    x=TOKENS.get(header[7:])
    if not x:raise PermissionError("invalid bearer token")
    return x
def scan_text(text:str)->dict:
    low=text.lower()
    return {
      "secret":any(p.search(text) for p in SECRET_PATTERNS),
      "pii":any(p.search(text) for p in PII_PATTERNS),
      "prompt_injection":any(x in low for x in INJECTION_MARKERS),
    }
def redact(text:str)->str:
    for p in SECRET_PATTERNS+PII_PATTERNS:text=p.sub("[REDACTED]",text)
    return text
