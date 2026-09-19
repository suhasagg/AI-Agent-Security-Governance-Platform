# Architecture

## Defense in depth
No single prompt classifier is the security boundary. The platform layers identity, tool exposure filtering, deterministic authorization, tool input/output guardrails, approval, DLP, rate limits and audit.

## Policy is outside the model
The model can request an action but cannot grant itself authorization. Authorization decisions are deterministic and use trusted identity, tenant, role, tool, arguments and environment.

## MCP governance
Tool filtering minimizes what a model can see. Tool guardrails inspect arguments and results. The MCP server remains a separate trust boundary and should independently authenticate the gateway in production.

## Approvals
Approval tokens are random, hashed at rest, time-limited, one-use and bound to the tenant plus a digest of exact tool arguments. A production system should additionally bind approver identity and separation-of-duties rules.

## Audit
Events are chained using SHA-256 over the previous event hash and canonical event data. This is tamper-evident, not magically tamper-proof: production should export chains to immutable/WORM storage or a transparency service.
