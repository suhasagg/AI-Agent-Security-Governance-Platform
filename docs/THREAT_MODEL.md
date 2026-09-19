# Threat model

Threats:
- direct prompt injection
- indirect injection from RAG/tool content
- secret exfiltration
- PII leakage
- confused deputy
- cross-tenant access
- excessive tool permissions
- malicious/poisoned MCP server
- tool-schema poisoning
- SSRF through tool arguments
- destructive actions
- approval bypass/replay
- runaway loops and cost abuse
- audit tampering
- compromised agent credentials

Controls:
- trusted identity context
- least privilege
- tool allowlists/filtering
- deterministic policy
- schema validation
- input/output tool guardrails
- human approval
- one-use bound approval tokens
- egress allowlists
- DLP
- rate/cost limits
- immutable audit export
- MCP server trust inventory and signing/provenance
