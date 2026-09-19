# AI Agent Security & Governance Platform


---

# Table of Contents

1. Executive Summary
2. Problem Statement
3. Security Objectives
4. Non-Goals
5. Core Security Invariants
6. Functional Requirements
7. Non-Functional Requirements
8. C4 Level 1 — System Context
9. C4 Level 2 — Container Architecture
10. Control Plane vs Enforcement Plane
11. Zero-Trust Reference Architecture
12. End-to-End Governed Agent Lifecycle
13. Trust Boundaries
14. Threat Actors
15. Asset Inventory
16. Identity Architecture
17. Human Identity
18. Agent Identity
19. Workload Identity
20. Tenant Identity
21. Authentication
22. Authorization Model
23. PEP / PDP / PIP Architecture
24. Policy Decision Contract
25. Policy Language and Policy-as-Code
26. Policy Lifecycle
27. Policy Versioning
28. Policy Testing
29. Agent Registration
30. Agent Manifest
31. Agent Risk Classification
32. Agent Lifecycle
33. Tool Registry
34. MCP Server Registry
35. MCP Trust Levels
36. Tool Discovery
37. Dynamic Tool Filtering
38. Discovery vs Invocation Authorization
39. Tool Schema Governance
40. Schema Fingerprinting
41. Schema Drift Detection
42. Tool Risk Classification
43. Semantic Argument Risk
44. Governance MCP Proxy
45. Tool Invocation State Machine
46. Pre-Execution Enforcement
47. Post-Execution Enforcement
48. Downstream Re-Authorization
49. Signed Execution Grants
50. Credential Brokerage
51. Short-Lived Credentials
52. Human Approval Architecture
53. Exact Approval Binding
54. Approval State Machine
55. Separation of Duties
56. Multi-Party Approval
57. Approval Replay Prevention
58. Approval Expiry and Revocation
59. Prompt Injection Defense
60. Indirect Prompt Injection
61. Tool Poisoning
62. MCP Server Compromise
63. Confused Deputy Prevention
64. Cross-Tenant Attack Prevention
65. Data Exfiltration Defense
66. DLP Architecture
67. PII and Secret Detection
68. Input Guardrails
69. Output Guardrails
70. Tool Guardrails
71. Guardrail Boundary Limitations
72. Untrusted Tool Output
73. Context Minimization
74. Memory Security
75. RAG Security
76. Retrieval ACL Enforcement
77. Data Classification
78. Data Residency
79. Network Security
80. Egress Control
81. SSRF Defense
82. Sandboxing
83. Code Execution Governance
84. Browser/Computer-Use Governance
85. Secrets Management
86. Key Rotation
87. Rate Limits and Quotas
88. Cost and Token Budgets
89. Runaway Agent Prevention
90. Loop Detection
91. Concurrency Controls
92. Idempotency
93. Ambiguous Mutation Recovery
94. Compensation and Recovery
95. Audit Architecture
96. Tamper-Evident Audit
97. Hash Chaining
98. Audit Event Schema
99. Non-Repudiation Considerations
100. Observability Architecture
101. Distributed Tracing
102. OpenTelemetry Alignment
103. Security Metrics
104. Governance Dashboards
105. SLOs and Security Invariants
106. Detection Engineering
107. Security Alerts
108. Incident Response Architecture
109. Kill Switches
110. Emergency Tool Revocation
111. Emergency Agent Revocation
112. Forensics
113. Evidence Retention
114. Evaluation Architecture
115. Security Evaluation
116. Prompt-Injection Evaluation
117. Tool-Authorization Evaluation
118. Approval Evaluation
119. Cross-Tenant Evaluation
120. DLP Evaluation
121. Agent Trajectory Evaluation
122. Red Team Program
123. Testing Strategy
124. Chaos Security Engineering
125. Supply-Chain Security
126. SBOM and Provenance
127. Dependency Governance
128. Container/Image Security
129. Kubernetes Architecture
130. Service Mesh and mTLS
131. Multi-Tenant Kubernetes Isolation
132. Multi-Region Architecture
133. Regional Policy Enforcement
134. Disaster Recovery
135. High Availability
136. Failure-Mode Matrix
137. Fail-Open vs Fail-Closed Matrix
138. Capacity Planning
139. Latency Budget
140. Cost Model
141. Backpressure
142. CI/CD Security Gates
143. Policy Deployment Pipeline
144. Tool Deployment Pipeline
145. Agent Deployment Pipeline
146. Model and Prompt Lifecycle
147. Schema and Protocol Versioning
148. MCP Evolution Strategy
149. Privacy and Retention
150. Compliance Mapping
151. Architecture Decision Records
152. Key Trade-Offs
153. Current Repository vs Target Architecture
154. Production Hardening Roadmap
155. Operational Runbooks
156. Principal Engineer Interview Walkthrough
157. Distinguished-Level Discussion Questions
158. Resume Positioning
159. Repository Guide
160. Local Development
161. Final Architecture Summary

---

# 1. Executive Summary

The AI Agent Security & Governance Platform is the **authoritative security control plane for autonomous and semi-autonomous AI systems**. Its job is not to make models trustworthy; its job is to ensure that untrusted probabilistic reasoning cannot exceed deterministic enterprise authority.

```text
User / Application
        |
   Identity Gateway
        |
   Agent Runtime
        |
  Dynamic Tool View
        |
        v
+---------------------------------------------------+
| GOVERNANCE ENFORCEMENT PROXY                      |
|                                                   |
| schema -> identity -> policy -> risk -> approval  |
| -> quota -> DLP -> credential grant -> dispatch   |
+----------------------+----------------------------+
                       |
                 Signed Execution Grant
                       |
                 MCP / Tool Plane
                       |
              Downstream Re-Authorization
                       |
                Enterprise Systems

Control Plane:
Agent Registry | Tool/MCP Registry | PDP | Policy Repo
Risk Engine | Approval Service | Credential Broker
Revocation | Audit | Security Analytics | Evaluation
```

The central invariant is:

> **The model may propose an action; only deterministic infrastructure may authorize, credential, execute and audit it.**

This corrects the most important weakness in the current scaffold: policy and approval cannot merely exist beside MCP invocation. **Every privileged invocation must traverse the enforcement proxy, and the downstream service must reject calls lacking a valid workload identity/execution grant.**

---

# 2. Problem Statement

Agent systems combine several security problems that traditional chatbots do not have:

```text
untrusted natural-language input
untrusted retrieved documents
probabilistic planning
dynamic tool discovery
machine credentials
cross-system side effects
long-lived memory
multi-agent delegation
human approvals
```

A prompt injection becomes materially dangerous when the model can turn attacker-controlled text into an authorized side effect. Therefore the architecture must assume the model, prompt, retrieved content, tool descriptions and tool outputs can all be manipulated.

---

# 3. Security Objectives

The **Security Objectives** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 4. Non-Goals

The **Non-Goals** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 5. Core Security Invariants

1. **No model-generated field grants authority.**
2. **Every privileged tool invocation passes through the governance PEP.**
3. **Downstream tools re-authorize; the proxy is not the only lock.**
4. **Tenant/principal identity comes from authenticated infrastructure.**
5. **Credentials are issued after authorization and never shown to the model.**
6. **Approval binds to exact canonical arguments and is one-use.**
7. **Unknown tools/servers/schemas fail closed.**
8. **Untrusted content cannot change policy.**
9. **Cross-tenant data/tool access is an invariant violation, not an error-budget item.**
10. **Revocation must propagate faster than ordinary configuration.**
11. **Every privileged mutation has an audit trail and recovery strategy.**
12. **SDK guardrails are defense-in-depth, not the sole authorization perimeter.**

---

# 6. Functional Requirements

The **Functional Requirements** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 7. Non-Functional Requirements

The **Non-Functional Requirements** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 8. C4 Level 1 — System Context

```text
+-------------------+
| Users / AI Apps   |
+---------+---------+
          |
          v
+--------------------------------------------------+
| AI Agent Security & Governance Platform          |
| Identity | Policy | Approval | Credentials | DLP |
+---------+---------------------------+------------+
          |                           |
          v                           v
   Agent Runtimes               MCP / Tool Servers
                                      |
                                      v
                              Enterprise Systems
```

---

# 9. C4 Level 2 — Container Architecture

```text
                        Identity / API Gateway
                                |
                           Agent Runtime
                                |
                         Governance Proxy (PEP)
                                |
        +-----------+-----------+-----------+-----------+
        |           |           |           |           |
       PDP       Risk Engine  Approval    DLP      Rate/Budget
        |                       |
        +-----------+-----------+
                    |
             Credential Broker
                    |
             Signed Exec Grant
                    |
             MCP Gateway/Server
                    |
         Downstream AuthZ / Resource
                    |
              Enterprise System

Control Plane:
Agent Registry | Tool Registry | MCP Server Registry
Policy Git/Store | Schema Registry | Revocation Service
Audit Ledger | Security Analytics | Eval/Red Team
```

---

# 10. Control Plane vs Enforcement Plane

The **Control Plane vs Enforcement Plane** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 11. Zero-Trust Reference Architecture

Every hop authenticates and authorizes the previous hop.

```text
human -> app
app -> agent runtime
runtime -> governance proxy
proxy -> MCP/tool server
tool server -> enterprise API
```

Trust is not transitive. A valid agent session does not imply permission to call every tool; a valid proxy call does not imply permission to mutate every resource.

---

# 12. End-to-End Governed Agent Lifecycle

```text
1 authenticate human/service
2 establish tenant, principal, roles
3 load registered agent manifest
4 compute allowed tool view
5 model reasons over permitted capabilities
6 model proposes tool + arguments
7 governance proxy canonicalizes/schema-validates
8 PDP evaluates identity/resource/environment/policy
9 risk engine determines approval requirements
10 approval service validates exact bound approval
11 quota/budget/DLP checks
12 credential broker issues scoped short-lived credential
13 proxy signs execution grant
14 MCP/tool server verifies workload + grant
15 downstream resource re-authorizes
16 execute
17 output guardrail/DLP
18 append audit event + trace
19 return minimized result to model
```

---

# 13. Trust Boundaries

Treat as untrusted:
- user prompts;
- documents/RAG chunks;
- model output;
- model-generated tool arguments;
- tool descriptions from unapproved servers;
- tool output;
- web content;
- long-term memory writes;
- external event payloads.

Trusted control inputs include:
- authenticated identity;
- registry metadata;
- signed policy versions;
- approval decisions;
- credential broker;
- revocation state;
- execution-grant signing keys.

---

# 14. Threat Actors

The **Threat Actors** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 15. Asset Inventory

The **Asset Inventory** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 16. Identity Architecture

The **Identity Architecture** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 17. Human Identity

The **Human Identity** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 18. Agent Identity

The **Agent Identity** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 19. Workload Identity

The **Workload Identity** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 20. Tenant Identity

The **Tenant Identity** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 21. Authentication

The **Authentication** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 22. Authorization Model

The **Authorization Model** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 23. PEP / PDP / PIP Architecture

```text
Agent -> PEP (Governance Proxy)
          |
          +-> PIP: identity, groups, resource, tenant, classification
          |
          +-> PDP: evaluate policy
          |
          `-> decision: ALLOW / DENY / REQUIRE_APPROVAL
```

The PEP is unavoidable in the network/tool topology. An application cannot choose to bypass it for convenience.

---

# 24. Policy Decision Contract

Example:

```json
{
  "decision": "REQUIRE_APPROVAL",
  "policy_version": "pol-1842",
  "risk": "HIGH",
  "constraints": {
    "max_amount": 5000,
    "allowed_region": "IN"
  },
  "obligations": [
    "redact_output",
    "audit_full_metadata"
  ]
}
```

The decision is structured and deterministic. Free-form LLM prose is not an authorization decision.

---

# 25. Policy Language and Policy-as-Code

The **Policy Language and Policy-as-Code** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 26. Policy Lifecycle

The **Policy Lifecycle** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 27. Policy Versioning

The **Policy Versioning** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 28. Policy Testing

The **Policy Testing** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 29. Agent Registration

The **Agent Registration** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 30. Agent Manifest

The **Agent Manifest** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 31. Agent Risk Classification

The **Agent Risk Classification** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 32. Agent Lifecycle

The **Agent Lifecycle** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 33. Tool Registry

Each tool record includes:

```text
canonical name
server
schema version/hash
owner
risk
read/write
resource types
required scopes
approval rule
idempotency support
compensation
timeout
data classification
allowed regions
status
```

Lifecycle:

```text
DISCOVERED -> QUARANTINED -> REVIEWED -> ACTIVE
-> DEPRECATED -> REVOKED
```

---

# 34. MCP Server Registry

The **MCP Server Registry** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 35. MCP Trust Levels

Example trust tiers:

```text
T0 untrusted/unknown        never exposed
T1 sandbox/dev              read-only constrained
T2 enterprise verified     approved scopes
T3 privileged              explicit approvals/strong isolation
```

A server becoming unreachable or changing schema does not automatically inherit previous trust.

---

# 36. Tool Discovery

The **Tool Discovery** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 37. Dynamic Tool Filtering

The model-visible set is:

```text
registered
∩ server trusted
∩ tenant allowed
∩ principal allowed
∩ agent allowed
∩ environment allowed
∩ regional policy
∩ current revocation state
∩ task relevance
```

This minimizes attack surface and model confusion. But filtering is not authorization; invocation is re-checked.

---

# 38. Discovery vs Invocation Authorization

A tool appearing in `list_tools` means:

```text
the model may consider it
```

not:

```text
the caller is authorized for every possible argument/resource
```

Invocation authorization evaluates exact arguments and target resources at call time.

---

# 39. Tool Schema Governance

The **Tool Schema Governance** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 40. Schema Fingerprinting

Canonicalize the JSON schema and compute:

```text
schema_hash = SHA-256(canonical_schema)
```

Registry approval binds to this hash. Unexpected schema drift moves the tool/server to quarantine or blocks privileged calls until reviewed.

---

# 41. Schema Drift Detection

The **Schema Drift Detection** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 42. Tool Risk Classification

The **Tool Risk Classification** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 43. Semantic Argument Risk

Schema validity is necessary but insufficient.

Example:

```text
scale_service(replicas=3)  -> low/medium
scale_service(replicas=300)-> high
```

Risk evaluates semantics:
- amount;
- environment;
- blast radius;
- resource sensitivity;
- destructive flags;
- destination domain;
- number of affected objects.

---

# 44. Governance MCP Proxy

This is the critical architectural component missing from simplistic agent-security demos.

```text
Agent MCP Client
     |
Governance MCP Proxy
     |
     + schema
     + identity
     + tenant
     + policy
     + risk
     + approval
     + budget
     + DLP
     + credential
     + audit
     |
Approved MCP Server
```

Network/service identity rules ensure privileged servers accept calls only from the proxy or another equivalent enforcement workload.

---

# 45. Tool Invocation State Machine

```text
REQUESTED
 -> SCHEMA_VALIDATED
 -> AUTHENTICATED
 -> AUTHORIZED
 -> APPROVAL_PENDING?
 -> APPROVED
 -> CREDENTIALIZED
 -> DISPATCHED
 -> ACKNOWLEDGED
 -> OUTPUT_VALIDATED
 -> AUDITED
 -> COMPLETED
```

Exceptional states:

```text
DENIED
REVOKED
EXPIRED
UNKNOWN_OUTCOME
COMPENSATING
FAILED
```

---

# 46. Pre-Execution Enforcement

The **Pre-Execution Enforcement** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 47. Post-Execution Enforcement

The **Post-Execution Enforcement** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 48. Downstream Re-Authorization

The **Downstream Re-Authorization** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 49. Signed Execution Grants

After policy and approval:

```json
{
  "tenant":"t1",
  "principal":"u42",
  "agent":"a7",
  "tool":"ops.rollback",
  "args_hash":"...",
  "resource":"svc/payments",
  "environment":"prod",
  "policy_version":"1842",
  "expires_at":"...",
  "nonce":"..."
}
```

The proxy signs the grant. The downstream tool verifies signature, expiry, nonce, audience and argument/resource binding before execution.

This prevents a compromised runtime from directly invoking the privileged tool with arbitrary arguments.

---

# 50. Credential Brokerage

Credentials are minted/retrieved only after authorization:

```text
approved invocation
 -> broker
 -> short-lived, audience/resource-scoped credential
 -> tool server
```

The model receives neither the credential nor a reusable token. Prefer workload identity/OAuth/mTLS over static secrets.

---

# 51. Short-Lived Credentials

The **Short-Lived Credentials** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 52. Human Approval Architecture

The **Human Approval Architecture** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 53. Exact Approval Binding

Approval binds:

```text
tenant
principal/requester
agent
tool
server
canonical args hash
resource
environment
policy version
expiry
nonce
approver
```

Any material change invalidates it. Approval is consumed once for mutation unless policy explicitly defines another scope.

---

# 54. Approval State Machine

The **Approval State Machine** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 55. Separation of Duties

Policies can enforce:

```text
requester != approver
agent owner != policy approver
tool publisher != tool security reviewer
```

High-risk actions can require two independent human approvals.

---

# 56. Multi-Party Approval

The **Multi-Party Approval** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 57. Approval Replay Prevention

The **Approval Replay Prevention** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 58. Approval Expiry and Revocation

The **Approval Expiry and Revocation** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 59. Prompt Injection Defense

Prompt injection cannot be solved reliably by a better system prompt.

Defense stack:

```text
minimize capabilities
separate instructions/evidence
untrusted-content labeling
tool filtering
deterministic authorization
credential isolation
egress controls
DLP
approval
audit
adversarial evaluation
```

Even a successfully injected model should still lack authority to exceed policy.

---

# 60. Indirect Prompt Injection

The **Indirect Prompt Injection** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 61. Tool Poisoning

Threats include malicious tool names/descriptions, changed schemas and malicious outputs.

Controls:
- trusted server registry;
- schema fingerprint;
- namespacing;
- owner/security review;
- signed artifacts;
- output schema validation;
- content/DLP guardrails;
- emergency revocation.

---

# 62. MCP Server Compromise

The **MCP Server Compromise** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 63. Confused Deputy Prevention

The agent/proxy must not use its own broad service authority to perform an action the end user could not perform.

Authorization includes both:
```text
end-user/principal context
AND
gateway/tool workload identity
```

Tenant/resource ownership is resolved from trusted systems, not model arguments.

---

# 64. Cross-Tenant Attack Prevention

The **Cross-Tenant Attack Prevention** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 65. Data Exfiltration Defense

Exfiltration paths:
- tool arguments;
- tool output;
- URLs;
- model response;
- traces/logs;
- memory;
- external connectors.

Controls include classification, DLP, destination allowlists, egress proxy, redaction, maximum response sizes and secret isolation.

---

# 66. DLP Architecture

The **DLP Architecture** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 67. PII and Secret Detection

The **PII and Secret Detection** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 68. Input Guardrails

The **Input Guardrails** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 69. Output Guardrails

The **Output Guardrails** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 70. Tool Guardrails

The **Tool Guardrails** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 71. Guardrail Boundary Limitations

Framework guardrails are valuable defense-in-depth, but architecture must respect their execution boundaries.

Agent-level input/output checks may apply only at specific workflow boundaries. Tool guardrails can protect supported local/function tool paths, while hosted/built-in tool paths may have different enforcement behavior.

Therefore **enterprise authorization cannot depend solely on SDK guardrails**. The independent governance proxy and downstream authorization remain authoritative.

---

# 72. Untrusted Tool Output

The **Untrusted Tool Output** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 73. Context Minimization

The **Context Minimization** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 74. Memory Security

The **Memory Security** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 75. RAG Security

RAG is an authorization system as well as a relevance system.

```text
identity/groups
 -> mandatory tenant/ACL/classification filter
 -> candidate retrieval
 -> ranking
 -> model context
```

Never retrieve all tenant data and ask the model to hide forbidden chunks.

---

# 76. Retrieval ACL Enforcement

The **Retrieval ACL Enforcement** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 77. Data Classification

The **Data Classification** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 78. Data Residency

The **Data Residency** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 79. Network Security

Privileged MCP/tool services are not publicly reachable from arbitrary agent pods.

Use:
- private network;
- service mesh/mTLS;
- workload identity;
- network policies;
- egress proxy;
- DNS restrictions;
- destination allowlists.

The governance proxy becomes an enforced network choke point.

---

# 80. Egress Control

The **Egress Control** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 81. SSRF Defense

Do not expose generic `fetch_url` capabilities to privileged agents without strict controls.

Use a fetch service with:
- scheme allowlist;
- DNS/IP validation;
- private/link-local blocking;
- redirect re-validation;
- response-size limit;
- MIME policy;
- audit.

---

# 82. Sandboxing

The **Sandboxing** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 83. Code Execution Governance

The **Code Execution Governance** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 84. Browser/Computer-Use Governance

The **Browser/Computer-Use Governance** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 85. Secrets Management

The **Secrets Management** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 86. Key Rotation

The **Key Rotation** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 87. Rate Limits and Quotas

The **Rate Limits and Quotas** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 88. Cost and Token Budgets

The **Cost and Token Budgets** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 89. Runaway Agent Prevention

Per run:

```text
max turns
max tool calls
max mutations
max tokens
max cost
max wall time
max parallel tools
```

Also detect repeated identical/near-identical calls and cyclic agent handoffs.

---

# 90. Loop Detection

The **Loop Detection** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 91. Concurrency Controls

The **Concurrency Controls** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 92. Idempotency

The **Idempotency** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 93. Ambiguous Mutation Recovery

Timeout after dispatch means outcome may be unknown.

```text
stable idempotency key
 -> query downstream operation/resource
 -> reconcile
 -> retry only if safe
```

Never assume timeout means the mutation failed.

---

# 94. Compensation and Recovery

The **Compensation and Recovery** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 95. Audit Architecture

Audit privileged events:

```text
identity/tenant
agent + version
tool/server/schema hash
canonical args digest
resource
policy decision/version
risk
approval ID/approver
credential grant ID
dispatch/result
trace ID
timestamp
```

Sensitive argument values may be encrypted/tokenized rather than logged in plaintext.

---

# 96. Tamper-Evident Audit

Hash-chain events:

```text
H_n = SHA256(H_(n-1) || canonical_event_n)
```

Periodically anchor checkpoints in a separately protected store/signature system.

Hash chaining detects tampering; it does not by itself provide authorization, availability or legal non-repudiation.

---

# 97. Hash Chaining

The **Hash Chaining** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 98. Audit Event Schema

The **Audit Event Schema** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 99. Non-Repudiation Considerations

The **Non-Repudiation Considerations** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 100. Observability Architecture

```text
agent.run
 |
 +-- policy.evaluate
 +-- approval.wait
 +-- credential.issue
 +-- tool.invoke
 |    +-- downstream.authz
 |    `-- enterprise.api
 +-- output.dlp
 `-- audit.append
```

Correlate agent trace IDs with governance invocation IDs without placing secrets/raw sensitive content into telemetry.

---

# 101. Distributed Tracing

The **Distributed Tracing** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 102. OpenTelemetry Alignment

The **OpenTelemetry Alignment** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 103. Security Metrics

Examples:
- denied tool calls;
- approval-required rate;
- approval replay attempts;
- schema drift;
- revoked-server attempts;
- cross-tenant denials;
- DLP blocks;
- prompt-injection detections;
- unknown-outcome mutations;
- tool-call loops;
- credential issuance failures;
- policy latency/p99.

---

# 104. Governance Dashboards

The **Governance Dashboards** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 105. SLOs and Security Invariants

Operational SLOs can have error budgets; security invariants do not.

```text
unauthorized privileged execution = 0
cross-tenant data release = 0
valid approval for governed high-risk mutations = 100%
audit coverage of privileged mutations = 100%
```

Availability SLOs should never justify bypassing these controls.

---

# 106. Detection Engineering

The **Detection Engineering** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 107. Security Alerts

The **Security Alerts** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 108. Incident Response Architecture

The **Incident Response Architecture** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 109. Kill Switches

Emergency controls:
- revoke agent;
- revoke tool;
- revoke MCP server;
- disable mutation class;
- disable tenant action plane;
- revoke credential audience;
- block destination domain;
- force read-only mode.

Revocation distribution is a high-priority control-plane path with aggressive cache invalidation.

---

# 110. Emergency Tool Revocation

The **Emergency Tool Revocation** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 111. Emergency Agent Revocation

The **Emergency Agent Revocation** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 112. Forensics

The **Forensics** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 113. Evidence Retention

The **Evidence Retention** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 114. Evaluation Architecture

```text
Versioned Security Scenario
 -> Agent Runtime
 -> Governance Proxy
 -> Simulated/Realistic Tool Plane
 -> Trace + Policy/Audit Events
 -> deterministic security graders
 -> trajectory graders
 -> regression gate
```

Evaluate enforcement, not merely whether the model “refused” in prose.

---

# 115. Security Evaluation

The **Security Evaluation** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 116. Prompt-Injection Evaluation

The **Prompt-Injection Evaluation** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 117. Tool-Authorization Evaluation

Adversarial cases:
- unauthorized tool;
- authorized tool/wrong resource;
- changed args after approval;
- wrong tenant;
- revoked tool;
- schema drift;
- expired grant;
- replayed nonce;
- direct server bypass.

Expected result: deterministic denial.

---

# 118. Approval Evaluation

Test:
```text
approval replay
approval substitution
expired approval
wrong approver
requester self-approval
changed arguments
changed environment
changed policy version
```

High-risk mutations should execute only under exact valid binding.

---

# 119. Cross-Tenant Evaluation

The **Cross-Tenant Evaluation** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 120. DLP Evaluation

The **DLP Evaluation** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 121. Agent Trajectory Evaluation

Inspect:
- model turns;
- attempted forbidden tools;
- policy denials;
- approval handling;
- retries;
- handoffs;
- exfiltration attempts;
- final result.

A model may fail the reasoning test but the **platform must still pass the security test** by containing it.

---

# 122. Red Team Program

The **Red Team Program** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 123. Testing Strategy

The **Testing Strategy** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 124. Chaos Security Engineering

The **Chaos Security Engineering** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 125. Supply-Chain Security

Govern:
- MCP server source/artifact;
- agent code;
- container images;
- Python/Java dependencies;
- policy bundles;
- model/tool schemas.

Use pinned dependencies, SBOM, vulnerability scanning, signed images/artifacts, provenance attestations and controlled promotion.

---

# 126. SBOM and Provenance

The **SBOM and Provenance** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 127. Dependency Governance

The **Dependency Governance** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 128. Container/Image Security

The **Container/Image Security** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 129. Kubernetes Architecture

```text
                    API / Identity Gateway
                            |
                      Agent Runtime Pods
                            |
                  Governance Proxy (PEP)
                            |
              +-------------+-------------+
              |                           |
          PDP/Policy                Approval Service
              |                           |
              +-------------+-------------+
                            |
                    Credential Broker
                            |
                     MCP Tool Plane
                            |
                     Enterprise APIs

Audit Pipeline | OTel | SIEM | Registry | Revocation
```

Use namespaces/network policies/service accounts/workload identity and dedicated pools for privileged tool workloads.

---

# 130. Service Mesh and mTLS

The **Service Mesh and mTLS** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 131. Multi-Tenant Kubernetes Isolation

The **Multi-Tenant Kubernetes Isolation** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 132. Multi-Region Architecture

The **Multi-Region Architecture** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 133. Regional Policy Enforcement

The **Regional Policy Enforcement** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 134. Disaster Recovery

The **Disaster Recovery** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 135. High Availability

The **High Availability** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 136. Failure-Mode Matrix

| Failure | Secure behavior |
|---|---|
| PDP unavailable | fail closed for privileged actions |
| approval service unavailable | wait/deny |
| credential broker unavailable | deny execution |
| audit sink unavailable | buffer or block critical mutations per policy |
| revocation service stale | short TTL + conservative policy |
| tool schema changes | quarantine/block |
| MCP server unavailable | fail/retry safely |
| model compromised/injected | policy still contains authority |
| proxy unavailable | privileged server remains unreachable directly |
| DLP unavailable | fail closed for restricted exfiltration paths |

---

# 137. Fail-Open vs Fail-Closed Matrix

```text
Authentication        CLOSED
Authorization         CLOSED
High-risk approval    CLOSED
Credential issuance   CLOSED
Schema verification   CLOSED
Revocation            CLOSED/conservative
Telemetry export      may degrade
Dashboard             may degrade
Non-security analytics may degrade
```

Make these choices explicit before incidents.

---

# 138. Capacity Planning

The **Capacity Planning** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 139. Latency Budget

The **Latency Budget** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 140. Cost Model

The **Cost Model** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 141. Backpressure

The **Backpressure** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 142. CI/CD Security Gates

The **CI/CD Security Gates** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 143. Policy Deployment Pipeline

The **Policy Deployment Pipeline** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 144. Tool Deployment Pipeline

The **Tool Deployment Pipeline** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 145. Agent Deployment Pipeline

The **Agent Deployment Pipeline** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 146. Model and Prompt Lifecycle

The **Model and Prompt Lifecycle** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 147. Schema and Protocol Versioning

The **Schema and Protocol Versioning** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 148. MCP Evolution Strategy

The **MCP Evolution Strategy** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 149. Privacy and Retention

The **Privacy and Retention** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 150. Compliance Mapping

The **Compliance Mapping** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 151. Architecture Decision Records

## ADR-001 — Mandatory governance proxy
All privileged tool calls traverse a PEP.

## ADR-002 — Downstream execution grants
Defense against runtime/proxy-bypass attempts.

## ADR-003 — Policy outside LLM
Probabilistic reasoning cannot grant authority.

## ADR-004 — Exact one-use approvals
Prevents replay/substitution.

## ADR-005 — Credentials after authorization
Secrets never enter model context.

## ADR-006 — Schema fingerprints
Detect tool drift/poisoning.

## ADR-007 — ACL before RAG context
Unauthorized data never reaches the model.

## ADR-008 — SDK guardrails are defense-in-depth
Framework boundaries are not universal authorization boundaries.

## ADR-009 — Revocation is a first-class fast path
Security response cannot wait for normal config TTLs.

## ADR-010 — Audit is semantic and tamper-evident
Tool mutations need reconstructable lineage.

---

# 152. Key Trade-Offs

The **Key Trade-Offs** subsystem is treated as a production security boundary with explicit ownership, contracts and failure semantics.

A Principal+/Distinguished design specifies:
- trusted and untrusted inputs;
- identity/tenant/resource scope;
- policy and authorization behavior;
- fail-open vs fail-closed choice;
- versioning and revocation;
- latency/capacity budget;
- privacy/retention;
- audit and observability;
- adversarial tests;
- operational response.

Security controls must remain effective during model error, prompt injection, stale caches, partial outages and deployment skew.

---

# 153. Current Repository vs Target Architecture

The current repository is an educational scaffold and has a **critical architectural gap**: policy/approval logic is not fully wired as an unavoidable enforcement point for every MCP invocation.

Current limitations to discuss transparently:
- an agent may be able to call a high-risk Java tool directly if the tool is visible;
- the Java tool plane does not fully enforce policy/approval/tenant identity;
- approval is not a cryptographically bound execution grant;
- downstream workload authentication is incomplete;
- tenant enforcement is incomplete;
- revocation, schema drift quarantine and credential brokerage are incomplete;
- audit is not a production immutable/tamper-evident ledger;
- prompt-injection/DLP controls are not a complete zero-trust boundary;
- Kubernetes/network isolation and supply-chain controls are not fully implemented;
- production-grade policy testing, red-team evaluation and SIEM integration are incomplete.

The target design fixes this with:

```text
Agent -> Mandatory Governance Proxy -> Signed Execution Grant
-> MCP Server Verification -> Downstream Re-Authorization
```

The README is a target architecture, not a claim that the scaffold already implements all controls.

---

# 154. Production Hardening Roadmap

### Phase 1
Central tool registry, tenant identity, deterministic policy.

### Phase 2
Mandatory governance proxy, network isolation, downstream workload auth.

### Phase 3
Exact approvals, signed execution grants, credential broker, idempotency.

### Phase 4
Schema fingerprints/drift quarantine, DLP, egress controls, tamper-evident audit.

### Phase 5
Fast revocation, SIEM/detection, red-team/eval platform, supply-chain signing.

### Phase 6
Multi-region policy/residency, HA/DR, compliance evidence automation and continuous adversarial testing.

---

# 155. Operational Runbooks

## Suspected prompt-injection-driven action
1. revoke affected agent/tool if necessary;
2. preserve trace/audit;
3. identify policy decision and grant;
4. inspect retrieved/tool content;
5. rotate credentials if exposed;
6. add adversarial regression case.

## Tool server compromised
1. emergency revoke server;
2. invalidate cached tool lists;
3. block network identity;
4. revoke credentials;
5. inspect all invocation grants/audit;
6. require new schema/artifact review.

## Cross-tenant suspicion
1. stop affected action/data paths;
2. preserve evidence;
3. validate identity/ACL/PDP inputs;
4. inspect caches and retrieval filters;
5. treat as security incident, not ordinary defect.

## Approval replay detected
Revoke approval/grants, inspect nonce store and audit, block mutation until integrity is restored.

---

1. How do you secure an agent even if its model is fully prompt-injected?
2. How do you make the policy enforcement point unavoidable?
3. Why must downstream tools re-authorize?
4. What should a signed execution grant contain?
5. How do you prevent grant replay?
6. How do you bind human approval to exact arguments?
7. How do you implement separation of duties?
8. How do you detect MCP schema drift?
9. How do you trust a newly discovered MCP server?
10. How do you prevent a confused deputy?
11. How do you enforce tenant identity end-to-end?
12. How do you keep credentials outside model context?
13. How do you prevent SSRF through tools?
14. How do you constrain browser/computer-use agents?
15. What are the limitations of SDK guardrails?
16. How do you protect against malicious tool output?
17. How do you secure RAG against cross-tenant leakage?
18. How do you make audit tamper-evident?
19. What fails closed when policy infrastructure is down?
20. How fast must emergency revocation propagate?
21. How do you handle an ambiguous mutating tool timeout?
22. How do you evaluate security if the model behaves nondeterministically?
23. How do you secure agent/tool software supply chains?
24. How do you enforce policy across multiple regions?
25. Which security properties are invariants rather than SLOs?

---

# 158. Portfolio Positioning

**AI Agent Security & Governance Platform** — Architected a zero-trust agent governance plane that assumes model compromise and makes prompt injection insufficient to gain enterprise authority. Designed mandatory MCP/tool enforcement proxies, PEP/PDP/PIP policy architecture, trusted agent/tool/server registries, schema fingerprints and drift quarantine, semantic risk classification, exact one-use human approvals, signed execution grants, downstream re-authorization, workload identity and short-lived credential brokerage, RAG ACL enforcement, egress/DLP controls, tamper-evident audit, fast revocation/kill switches, OTel/SIEM observability, adversarial trajectory evaluation, Kubernetes isolation and multi-region policy enforcement across Python agent runtimes and Java tool services.

---

# 159. Repository Guide

```text
ai-agent-security-governance-platform/
|
+-- python-governance/
|   +-- app/
|   |   +-- agent_runtime/
|   |   +-- gateway/
|   |   +-- policy/
|   |   +-- approvals/
|   |   +-- dlp/
|   |   +-- audit/
|   |   `-- main.py
|   +-- tests/
|   `-- Dockerfile
|
+-- java-mcp-tools/
|   +-- src/main/
|   +-- src/test/
|   `-- pom.xml
|
+-- policies/
+-- evals/
+-- docs/
+-- infra/
+-- docker-compose.yml
+-- Makefile
`-- README.md
```

---

# 160. Local Development

Typical scaffold:

```bash
cp .env.example .env
docker compose up --build
```

Local/demo approval endpoints and tenant headers are not production security controls. A production deployment must make the governance proxy unavoidable and require downstream workload identity/execution-grant verification.

---

# 161. Final Architecture Summary

A production AI Agent Security & Governance Platform should obey:

```text
1. ASSUME THE MODEL CAN BE PROMPT-INJECTED.
2. MAKE THE GOVERNANCE ENFORCEMENT PATH UNAVOIDABLE.
3. RE-AUTHORIZE AT THE DOWNSTREAM TOOL/RESOURCE.
4. NEVER ACCEPT MODEL-GENERATED AUTHORITY.
5. SEPARATE TOOL DISCOVERY FROM INVOCATION AUTHORIZATION.
6. TRUST ONLY REGISTERED, VERSIONED, SCHEMA-FINGERPRINTED TOOLS.
7. BIND APPROVAL TO EXACT ACTION + RESOURCE + EXPIRY + NONCE.
8. ISSUE CREDENTIALS ONLY AFTER AUTHORIZATION.
9. KEEP CREDENTIALS OUTSIDE MODEL CONTEXT.
10. APPLY TENANT/ACL SECURITY BEFORE RAG DATA REACHES THE MODEL.
11. TREAT TOOL OUTPUT AND RETRIEVED CONTENT AS UNTRUSTED.
12. FAIL CLOSED FOR IDENTITY, POLICY, APPROVAL AND REVOCATION.
13. MAKE PRIVILEGED ACTIONS AUDITABLE AND RECOVERABLE.
14. TEST THE PLATFORM WITH ADVERSARIAL AGENT TRAJECTORIES.
15. MAKE REVOCATION AND KILL SWITCHES FIRST-CLASS.
```

The defining principle is:

> **A secure agent platform does not require the model to be trustworthy; it requires the model to be unable to exceed deterministic authority.**

---
