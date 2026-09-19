# Production security checklist

- Replace static demo tokens with OAuth/OIDC JWT validation.
- Validate issuer, audience, expiry and scopes.
- Use workload identity or mTLS between governance gateway and MCP servers.
- Keep access tokens in authorization headers, never URLs or prompts.
- Authorize tenant access at every data/tool boundary.
- Use enterprise DLP rather than regex-only detection.
- Apply SSRF protection and outbound egress allowlists.
- Scan and register MCP servers before allowing agent access.
- Pin trusted tool schemas and detect unexpected schema changes.
- Redact sensitive values from traces and audit events.
- Separate approver and requester for critical operations.
- Make approvals exact-argument, expiring, nonce-bound and one-use.
- Store audit logs in immutable storage.
- Define incident response for model/tool compromise.
- Disable or redirect SDK tracing when privacy/ZDR requirements demand it.
