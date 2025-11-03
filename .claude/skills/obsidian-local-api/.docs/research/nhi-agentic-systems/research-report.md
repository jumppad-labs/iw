# Research Report: Non-Human Identities for Agentic Systems

**Research Period**: January 3, 2025
**Generated**: January 3, 2025
**Purpose**: Design feature in HashiCorp Vault to merge human identity (JWT) with vault agent identity for AI agentic frameworks

---

## Executive Summary

This research investigated how to implement a feature in HashiCorp Vault that merges human identity (JWT tokens) with vault agent identities, specifically targeting AI agentic frameworks like LangGraph. The study examined non-human identity (NHI) management across 34 industry sources, including standards specifications, cloud provider implementations, security frameworks, and AI agent platforms.

Non-human identities now outnumber human identities by 100:1 in modern enterprises, with credential abuse remaining the top attack vector. The research identified that all major cloud providers (AWS, Azure, GCP) implement hybrid identity patterns through delegation and impersonation mechanisms, with OAuth 2.0 Token Exchange (RFC 8693) emerging as the standardized approach. HashiCorp Vault's existing entity and entity alias system provides a strong foundation for implementing merged identities, with JWT authentication creating automatic entity alias mappings.

Key findings reveal that successful hybrid identity implementations require: (1) clear delegation vs. impersonation semantics, (2) time-bound composite identities with explicit expiration, (3) comprehensive audit trails showing human→agent attribution, (4) Just-In-Time (JIT) authorization for AI agents, and (5) compliance with SOC2 and HIPAA requirements through proper IAM controls and audit logging. The recommended architecture leverages Vault's entity system with composite entity aliases, JWT actor claims for delegation chains, session metadata for human context, and policy composition with explicit boundaries. This approach enables LangGraph and similar frameworks to operate with combined human-agent authorization while maintaining security, auditability, and compliance.

## Research Questions

### 1. How do modern identity systems handle non-human identities (NHI)?
Examined security models, authentication patterns, lifecycle management, and privilege models for service accounts, agents, and workloads.

### 2. What are the architectural patterns for merging human and machine identities?
Investigated delegation models, identity chaining, composite identity structures, and session management approaches.

### 3. How does HashiCorp Vault currently handle agent authentication?
Analyzed Vault auth methods (JWT, AppRole, Kubernetes), identity tokens, entity aliases, and policy attachment mechanisms.

### 4. What are the security implications of binding human JWT with agent identities?
Evaluated token lifecycle management, privilege escalation risks, audit requirements, and compliance considerations (SOC2, HIPAA).

### 5. How do other systems implement hybrid human-agent identity?
Compared AWS IAM, Azure Managed Identity, GCP Service Accounts, and SPIFFE/SPIRE implementations.

### 6. What are the specific challenges for AI agent identity in LangGraph and similar frameworks?
Studied agent execution context, human-in-the-loop authorization, multi-step workflow identity propagation, and compliance tracking.

---

## Key Findings

### The Non-Human Identity Crisis

**Scale and Growth** (Sources: #1, #31, #32)

The NHI landscape has reached critical mass, with non-human identities outnumbering human identities by 100:1 in 2024 enterprises. Cloud-native environments show ratios as high as 40,000:1. Despite this explosive growth, over 20% of NHIs remain insufficiently secured, creating a massive attack surface. Verizon's 2025 Data Breach Investigations Report confirms that credential abuse—primarily involving compromised API keys, service accounts, and automation credentials—remains the top initial attack vector (Sources: #1, #3).

**OWASP NHI Top 10 for 2025** (Source: #2)

The industry has responded with OWASP's first standardized framework for NHI security risks, highlighting: secret leakage, improper offboarding, overprivileged NHIs, insecure authentication, and human misuse of NHI. This represents a watershed moment where NHI security transitions from an overlooked area to a top priority, with 83% of organizations increasing security spend.

**Lifecycle Management Imperative** (Sources: #31, #32, #33)

Best practices converge on five pillars: (1) automated discovery and inventory management, (2) governance policies for provisioning with approval workflows, (3) continuous monitoring of usage patterns, (4) real-time anomaly detection, and (5) proper deprovisioning. The mantra for 2025: "Securing service accounts is no longer an optional best practice—it's a fundamental pillar of enterprise security."

### HashiCorp Vault: Foundation for Hybrid Identity

**Entity and Entity Alias Architecture** (Sources: #12, #13, #14)

Vault's identity system provides an elegant foundation for merged identities. An entity represents a unified identity that can have multiple entity aliases, each representing an account in a specific auth method (JWT, AppRole, Kubernetes, etc.). When a user authenticates via any method, the entity identifier is tied to the token, and all entity-level policies and metadata are inherited. This architecture naturally supports the concept of composite identities.

**JWT Authentication Integration** (Source: #12)

The JWT auth method uses the `user_claim` parameter to uniquely identify users and automatically creates entity aliases. Since Vault 1.16, the role name is available in alias metadata, enabling policy decisions based on authentication context. The method supports nested claims via JSON Pointers and requires at least one binding criterion (bound_audiences, bound_subject, bound_claims, or token_bound_cidrs) for security.

**Practical Implications**

Vault's existing architecture can be extended to support human-agent identity merging by: (1) creating a new entity alias type for composite identities, (2) binding human JWT claims with agent entity metadata, (3) leveraging role metadata to track delegation context, and (4) using policy inheritance to compose human and agent permissions with explicit boundaries.

### OAuth 2.0 Token Exchange: The Standard for Delegation

**RFC 8693 Foundation** (Sources: #4, #18, #19)

OAuth 2.0 Token Exchange (RFC 8693) defines the standardized approach for delegation and impersonation through Security Token Services (STS). The protocol uses grant_type `urn:ietf:params:oauth:grant-type:token-exchange` and supports exchanging one token type for another while preserving or transforming identity context. This is the de facto standard for API gateways and service-to-service communication acting on behalf of users.

**Delegation vs. Impersonation Semantics** (Sources: #18, #19)

The distinction is critical:

- **Delegation**: Principal A retains its own identity while representing Principal B. Actions are taken by A on behalf of B, maintaining attribution.
- **Impersonation**: Principal A assumes all rights of Principal B and is indistinguishable from B within that context. More powerful but higher risk.

For AI agentic systems, delegation is the appropriate pattern as it maintains clear attribution of agent actions to both the agent and the originating human.

**JWT Actor Claim** (Source: #18)

The `"act"` (actor) claim in JWTs provides the mechanism to express delegation chains. The claim identifies the acting party to whom authority has been delegated and supports nested actor claims for multi-hop delegation. This standard approach should be adopted for Vault's implementation.

**Security Considerations** (Sources: #18, #19)

Token exchange introduces abuse potential. Mitigations include: client authentication for additional STS authorization checks, scope limitation to restrict delegated permissions, time constraints through short-lived tokens, and comprehensive audit logging of all delegation events.

### Cloud Provider Hybrid Identity Patterns

**AWS IAM: Session Tags and Role Chaining** (Sources: #7, #8)

AWS implements hybrid identity through role assumption with session tags. Tags are key-value pairs passed during `sts:AssumeRole` that provide context about the delegation. Session tags can be made transitive to persist through role chaining, with precedence rules ensuring assumption-time values override role-attached values. The pattern requires explicit `sts:TagSession` permission in trust policies and supports conditional controls to restrict which tags can be set.

**Azure: Workload Identity Federation** (Source: #9)

Azure's approach eliminates secret management through federated credentials on user-assigned managed identities. External workloads present OIDC tokens (matching issuer and subject claims) which are exchanged for Azure access tokens. The system supports up to 20 federated credentials per identity and works across Kubernetes (on-prem, AKS, EKS, GKE), GitHub Actions, and any OIDC-compliant IdP. Propagation delays of a few seconds are normal after credential creation.

**GCP: Workload Identity Federation + Impersonation** (Sources: #10, #11)

GCP combines workload identity federation (following OAuth 2.0 token exchange) with service account impersonation. External credentials are exchanged for federated tokens, which can then be used to impersonate service accounts (producing 1-hour access tokens). IAM bindings reference external identities by subject, group, or custom attributes from the IdP. The two-stage process (federation → impersonation) provides flexibility and security boundaries.

**Comparative Analysis**

All three providers converge on similar patterns: (1) trust establishment with external IdPs via OIDC/SAML, (2) token exchange mechanisms, (3) short-lived resulting credentials, (4) attribute-based binding for fine-grained control, and (5) support for delegation chains. The differences lie primarily in API design and credential lifespan (AWS auto-rotating, Azure depending on source token, GCP fixed at 1 hour).

### SPIFFE/SPIRE: Workload Identity Standard

**Core Architecture** (Source: #5)

SPIFFE provides a framework for workload identity using SPIFFE IDs (URIs like `spiffe://trust-domain/workload-path`) and SVIDs (SPIFFE Verifiable Identity Documents). Two SVID types exist: X.509-SVID (preferred, resistant to replay attacks) and JWT-SVID (for Layer 7 proxy scenarios). Trust domains isolate workloads across security boundaries, with organizations maintaining distinct domains for different environments.

**Workload Attestation** (Source: #5)

SPIRE implements automatic identity issuance without pre-shared secrets. Node attestation authenticates agents, which then discover workload selectors (e.g., Unix kernel metadata) and assign appropriate SVIDs. Keys rotate automatically and frequently, with trust bundles containing public key material for cryptographic verification.

**Relevance to Vault Integration**

SPIFFE/SPIRE demonstrates that cryptographically-verifiable workload identity can be fully automated. For Vault's agent identity feature, adopting similar principles—automatic attestation, frequent rotation, and trust bundle distribution—would strengthen security posture.

### Security Implications and Token Management

**JWT Privilege Escalation Risks** (Sources: #15, #17)

The primary vulnerability in JWT-based systems is signature verification failure. Attackers exploiting this can modify token payloads to escalate privileges, leading to account takeover and data breaches. Common attack vectors include: payload manipulation with signature deletion, "none" algorithm exploits (where unsigned tokens are accepted), and weak secret cracking followed by re-signing.

**Token Lifecycle Best Practices** (Sources: #16, #17)

Industry consensus establishes: access tokens should last 15-30 minutes, refresh tokens maximum 7-14 days. Refresh token rotation (generating new refresh tokens on each use) prevents replay attacks through single-use tokens. The `jti` (JWT ID) claim enables tracking and revocation of specific tokens. Security best practices mandate: rejecting weak algorithms, enforcing 64+ character secrets from secure random sources, minimizing payload claims, storing tokens in HTTP-only cookies (not localStorage), and always including expiration (`exp`) claims.

**Advanced Security Measures** (Source: #17)

Production systems must: enforce strong signature algorithms (RS256, ES256), validate audience (`aud`) and issuer (`iss`) claims, check time-based claims (`nbf`, `iat`), rotate signing keys regularly, and implement comprehensive logging of all token operations.

**Implications for Vault Hybrid Identity**

When merging human JWT with agent identity, Vault must: validate all human JWT claims before merging, create new composite tokens with short lifespans, implement automatic rotation for merged identities, maintain separate audit trails for human and agent actions, and provide revocation mechanisms that can target either the human or agent component.

### Compliance Requirements: SOC2 and HIPAA

**Identity and Access Management Controls** (Sources: #25, #26)

Both frameworks require: least privilege access (minimal necessary permissions), multi-factor authentication for sensitive access, role-based access control (RBAC) with role definitions appropriate to the domain, encryption, and two-factor authentication. HIPAA adds healthcare-specific requirements, particularly for Protected Health Information (PHI) access controls.

**Audit Logging Requirements** (Sources: #25, #26)

SOC 2 mandates comprehensive logging of audit controls, API activity, and security events. HIPAA requires specific PHI access tracking: who accessed what PHI, when, and why, with long-term retention. Implementation typically uses CloudTrail (API activity) and CloudWatch (system performance and security events) or equivalent solutions.

**Framework Alignment and Dual Compliance** (Sources: #25, #26)

Organizations handling PHI can align SOC 2 controls with HIPAA requirements, as both share security and privacy goals requiring continuous compliance and independent audits. SOC 2 reports can be tailored to include HIPAA-relevant controls, providing a comprehensive data security posture.

**Token Lifecycle Compliance**

For merged human-agent identities, compliance demands: credential rotation, access expiration with time-limited tokens, complete audit trails of token issuance/usage/revocation, and token scopes reflecting minimum necessary access per least privilege principles.

**Implications for Vault Feature**

The Vault implementation must provide: comprehensive audit logging differentiating human vs. agent actions, support for time-limited composite identities with automatic expiration, role-based controls for which humans can merge with which agents, and API endpoints for compliance reporting and audit trail extraction.

### Identity Context Propagation in Distributed Systems

**End-to-End Identity Transmission** (Sources: #27, #30)

Modern microservices architectures maintain user context across service boundaries through end-to-end identity transmission. Benefits include enhanced security, elimination of generic privileged accounts, secure audit trails, and support for complex authentication scenarios. API gateways typically propagate identity via JWT in request headers, allowing downstream services to make authorization decisions and record attribution.

**W3C Trace Context Standard** (Sources: #29, #6)

The W3C Trace Context standard enables trace context (trace ID, span information) to propagate across heterogeneous distributed systems. Context propagation mechanisms pass unique identifiers and metadata with transactions, ensuring each service is aware of the end-to-end trace. This pattern applies equally to identity context, where the same propagation mechanisms can carry both tracing and identity information.

**Audit Trails in Microservices** (Source: #28)

Best practices favor platform-level audit functionality standardized across microservices regardless of technology stack. Common properties (userId, timestamp) are populated from request context, with a dedicated central microservice responsible for audit management. This provides a consolidated view of actions across the distributed system.

**Application to Vault Hybrid Identity**

When agents operate across distributed systems, the merged human-agent identity must propagate through the entire service chain. Vault should: generate composite JWTs with both human and agent claims, support W3C Trace Context for correlation, provide middleware/SDK for identity propagation, and ensure audit events from all services can be correlated back to the originating human-agent pair.

### AI Agent Identity and Authorization Challenges

**LangGraph Authentication and Authorization** (Sources: #20, #21, #22)

LangGraph distinguishes authentication (`@auth.authenticate` handlers verifying identity) from authorization (`@auth.on` handlers determining permissions). User identity is made available throughout the agent via `config["configuration"]["langgraph_auth_user"]`, enabling delegated access where agents receive user-scoped credentials to access resources on behalf of users.

**Human-in-the-Loop Patterns** (Sources: #20, #21)

LangGraph's built-in statefulness enables human-in-the-loop collaboration: agents draft responses and await approval before acting. Breakpoints interrupt agent sequences, allowing humans to resume later. Asynchronous authorization via CIBA (Client-Initiated Backchannel Authentication) provides a standardized mechanism for agents to request authorization without browser redirects, maintaining efficiency while keeping humans in control.

**Agent Authorization Best Practices** (Sources: #22, #23, #24)

The right approach uses OAuth-based agent authentication with just-in-time, least-privileged access. Dynamic tool authorization handles OAuth inside the agent loop, authorizing tools only when needed rather than requiring upfront pre-authorization of all services. Production systems should: limit permissions to application needs, use read-only credentials where possible, implement sandboxing, use credential management mechanisms (not long-lived secrets), and employ the four-perimeter security model: prompt protection, secure document retrieval, external action controls, and response enforcement.

**Authentication Flows for Agents** (Sources: #23, #24)

Common patterns include: Auth Code Flow (user-interactive), On-Behalf-Of Token Flow (agent acts on user's behalf), and Client Credentials Flow (private environment agent). For confidential agents, the client credentials flow is appropriate; for agents acting on behalf of users, the OBO flow (which aligns with OAuth 2.0 token exchange) is correct.

**Just-in-Time Security Model** (Sources: #22, #34)

Modern AI agent security replaces long-lived permissions with dynamic, event-driven access. The JIT model grants minimum required privilege only when needed and revokes it immediately after use. This aligns with zero trust principles and minimizes the window of compromise.

**Implications for Vault Hybrid Identity**

Vault's human-agent identity merging must support: (1) LangGraph's authentication handler integration, (2) Just-In-Time credential issuance for agent operations, (3) human-in-the-loop authorization flows including CIBA, (4) automatic revocation when agent workflow completes, (5) scope limitation based on both human permissions and agent role, and (6) comprehensive audit logging for compliance and debugging.

### Implementation Patterns for Merged Identities

**Centralized Identity Provider Pattern** (Source: #30)

A single identity provider acts as the source of truth for all services, managing authentication, identity information, roles, and permissions. Benefits include consistency across services, simplified administration, and centralized audit trails. For Vault, this pattern suggests that Vault should be the authoritative source for merged identities, with services integrating via Vault's API.

**Token-Based Identity Distribution** (Source: #30)

When all services understand JWT validation, the identity mechanism becomes distributed. Front-facing proxies convert reference tokens (opaque) to value tokens (JWTs) which are then distributed throughout the internal network. This reduces bottlenecks and enables horizontal scaling.

**Chained Microservice Pattern** (Source: #30)

In service chains (A → B → C), identity context must propagate through each hop. Implementation typically uses synchronous HTTP with identity in headers, though the same pattern applies to async messaging with identity in message metadata. For merged identities, both human and agent contexts must propagate together.

**Composite Identity Pattern**

The composite pattern explicitly creates a merged identity object combining human and agent contexts. Implementation approaches include: API gateway handling aggregation, service mesh managing propagation, facade services presenting unified identity, or explicit composite identity tokens. For Vault, the composite pattern implemented through enhanced entity aliases with both human JWT claims and agent metadata is the natural fit.

**Federated Identity Pattern** (Source: #30)

Delegating authentication to external trusted IdPs eliminates credential storage requirements and enables SSO and external integration. Azure's workload identity federation exemplifies this pattern. For Vault's use case, the human JWT comes from an external IdP (Auth0, Okta, etc.), while the agent identity is Vault-native, requiring trust establishment between Vault and the external IdP.

---

## Detailed Analysis by Research Question

### Question 1: How do modern identity systems handle non-human identities?

**Summary**: Modern NHI management has evolved from ad-hoc practices to structured lifecycle approaches with automated discovery, governance policies, least privilege enforcement, and real-time monitoring.

**Key Findings**:

The NHI landscape has reached crisis proportions, with identities outnumbering humans 100:1 and 20% remaining insufficiently secured (Sources: #1, #31). OWASP's 2025 NHI Top 10 provides the first industry-standard security framework, identifying secret leakage, improper offboarding, overprivileged NHIs, insecure authentication, and human misuse as top risks (Source: #2).

Best-in-class implementations follow a five-pillar approach (Sources: #31, #32, #33):

1. **Discovery and Visibility**: Automated tools detect NHIs across cloud and on-premises, maintaining real-time inventory
2. **Lifecycle Governance**: Approval workflows for provisioning, continuous monitoring, proper deprovisioning
3. **Least Privilege**: RBAC/ABAC with minimal permissions, dynamic restrictions based on context
4. **Credential Security**: Regular rotation, secure storage in secrets managers, real-time anomaly detection
5. **Human Misuse Prevention**: Dedicated human identities for debugging, audit tracking, accountability mechanisms

The shift from 2024 to 2025 marks NHI security transitioning from overlooked to fundamental, with 83% of organizations increasing spending (Source: #1).

**Analysis**:

The explosive growth of NHIs reflects cloud adoption, containerization, microservices, and now AI agents. Each service, pod, function, and agent requires identity, creating an identity explosion that traditional IAM systems weren't designed to handle. The OWASP NHI Top 10 codifies learnings from breaches where compromised service accounts enabled lateral movement and data exfiltration.

The focus on lifecycle management addresses the core problem: NHIs are often created but rarely removed, accumulating as "ghost" identities with unknown access. Automated discovery solves visibility; governance solves creation; monitoring solves detection; deprovisioning solves cleanup.

Credential rotation addresses the fundamental weakness of long-lived secrets. Services accessing APIs with year-old credentials provide attackers persistent access once compromised. Rotation limits compromise windows; secrets managers prevent credentials in code repositories.

**Implications for Vault Feature**:

Vault's agent identities must integrate with these lifecycle practices. The merged human-agent identity should: auto-expire based on policy, support discovery APIs for inventory tools, integrate with monitoring for anomaly detection, and enable proper deprovisioning when agents or human access should be revoked.

### Question 2: What are the architectural patterns for merging human and machine identities?

**Summary**: OAuth 2.0 Token Exchange (RFC 8693) provides the standard mechanism for identity delegation and impersonation, with delegation semantics (maintaining separate identities) being appropriate for AI agents to preserve attribution.

**Key Findings**:

RFC 8693 defines token exchange using grant_type `urn:ietf:params:oauth:grant-type:token-exchange` with parameters for subject tokens, scopes, and audience (Sources: #4, #18). The standard explicitly addresses delegation and impersonation as distinct patterns:

**Delegation**: Principal A represents Principal B while maintaining its own identity. Actions are by A on behalf of B. Appropriate for service-to-service calls, API gateways, and AI agents.

**Impersonation**: Principal A assumes B's full identity and is indistinguishable from B. Higher risk but necessary for specific scenarios like administrative troubleshooting.

The JWT `"act"` (actor) claim standardizes delegation expression, identifying the acting party and supporting nested claims for delegation chains (Source: #18). Security considerations include client authentication for STS authorization checks, scope limitation, and time-bounded tokens (Sources: #18, #19).

Cloud providers implement these patterns differently:
- **AWS**: Session tags with role assumption, transitive tags for chaining (Sources: #7, #8)
- **Azure**: Federated credentials on managed identities (Source: #9)
- **GCP**: Workload identity federation + service account impersonation (Sources: #10, #11)

All converge on: trust establishment, token exchange, short-lived credentials, attribute-based control.

**Analysis**:

The delegation vs. impersonation distinction is critical for AI agents. Impersonation erases attribution—actions appear to come from the human, making it impossible to determine if a human or agent performed an action. This creates audit and compliance nightmares. Delegation maintains dual attribution: the agent performed the action on behalf of the human.

The `"act"` claim provides the mechanism. A JWT might have `"sub": "human-user-123"` and `"act": {"sub": "agent-xyz"}`, explicitly showing the agent acting for the human. Audit logs can track both identities, security policies can restrict agent capabilities beyond human permissions, and anomaly detection can identify suspicious agent behavior.

Session tags (AWS) and federated credentials (Azure, GCP) show different approaches to the same goal: binding external identity with internal identity while preserving context. AWS favors tags as metadata; Azure/GCP favor token exchange. Both work; the choice depends on existing infrastructure.

Short-lived credentials appear universally—typically 1 hour or less. This limits compromise windows and forces regular re-authentication, catching revocation events quickly.

**Implications for Vault Feature**:

Vault should adopt delegation semantics with JWT actor claims. When a human JWT is merged with an agent entity, the resulting token should have:
- `sub`: Agent identity (the actual actor)
- `act.sub`: Human identity (the delegating principal)
- `scope`: Intersection of human and agent permissions, or human permissions with agent-specific restrictions
- `exp`: Short TTL (15-30 minutes)
- `jti`: Unique ID for tracking and revocation

Vault's entity system can represent this: the entity is the agent, with an entity alias created from the human JWT, and metadata storing the delegation context.

### Question 3: How does HashiCorp Vault currently handle agent authentication?

**Summary**: Vault's entity and entity alias system provides a robust foundation for unified identity across multiple auth methods, with JWT auth automatically creating entity aliases based on token claims.

**Key Findings**:

Vault's identity model centers on entities and entity aliases (Sources: #12, #13, #14):
- **Entity**: Represents a unified identity (typically a user or service)
- **Entity Alias**: Maps a specific auth method account to an entity
- **Policy Inheritance**: Entity-level policies and metadata are inherited by all aliases
- **Token Linkage**: Entity ID is attached to tokens after authentication

JWT auth configuration uses:
- `user_claim` (required): Claim for entity alias name (typically `sub`)
- `role_type`: "jwt" or "oidc"
- `bound_audiences`: Required aud claim matching
- Binding requirements: At least one of bound_audiences, bound_subject, bound_claims, or token_bound_cidrs

Since Vault 1.16, role names are available in alias metadata under the `role` key, enabling policy decisions based on authentication context (Source: #12).

Entity aliases are created automatically on successful JWT auth. The alias name is the value of the `user_claim` from the token, and the alias is linked to an entity (either existing or newly created).

**Analysis**:

Vault's architecture elegantly solves multi-auth-method identity. A developer might authenticate via GitHub in development, LDAP in corporate environment, and JWT from CI/CD. All map to the same entity, inheriting the same policies.

This design extends naturally to hybrid identities. An agent entity could have:
1. Primary alias: AppRole auth (native agent identity)
2. Secondary alias: JWT auth with human token (delegated identity)

When authenticating with the merged identity, both aliases would be active, both sets of metadata available, and policies could be composed.

The role metadata feature (Vault 1.16+) enables context-aware policies. A policy could distinguish between direct agent access and human-delegated agent access, applying different permissions based on the role used.

The automatic alias creation simplifies integration—no separate API calls to establish the human-agent link, just authenticate with the appropriate role configured to create the correct alias type.

**Implementation Considerations**:

Vault needs a new concept: **composite entity alias** or **delegated entity alias**. This special alias type would:
- Store both agent identity (entity) and human identity (JWT claims)
- Have a TTL matching the human JWT or shorter
- Include metadata showing delegation context (timestamp, human ID, original JWT ID)
- Support revocation targeting either human or agent component

Policy language might extend to reference delegation: `path "secret/data/*" { capabilities = ["read"] } when entity.alias.type == "delegated" and entity.delegation.human.sub == "approved-user"`

### Question 4: What are the security implications of binding human JWT with agent identities?

**Summary**: Merging identities introduces privilege escalation risks, requires strict token lifecycle management, demands comprehensive audit logging, and must comply with SOC2/HIPAA requirements for IAM and audit trails.

**Key Findings**:

**Privilege Escalation Risks** (Sources: #15, #17):
- Signature verification failures enable payload modification and privilege escalation
- Attack vectors: payload manipulation, "none" algorithm exploits, weak secret cracking
- Impact: Account takeover, privilege escalation, data breaches

**Token Lifecycle Requirements** (Sources: #16, #17):
- Access tokens: 15-30 minutes
- Refresh tokens: 7-14 days maximum
- Refresh token rotation prevents replay attacks
- `jti` claim enables tracking and revocation
- Strong secrets (64+ chars), secure storage (HTTP-only cookies), always include `exp`

**Compliance Requirements** (Sources: #25, #26):
- SOC2 & HIPAA: Least privilege, MFA, RBAC, comprehensive audit logging
- HIPAA adds PHI-specific access tracking and healthcare role definitions
- Audit logging must capture: who accessed what, when, why, and result
- CloudTrail and CloudWatch (or equivalent) are foundational

**Security Best Practices** (Source: #17):
- Enforce strong algorithms (RS256, ES256)
- Validate all claims: aud, iss, exp, nbf, iat
- Regular key rotation
- Never store in localStorage (XSS vulnerable)

**Analysis**:

Merging human and agent identities amplifies existing JWT security concerns. If an attacker compromises the merged identity, they gain both human and agent capabilities—potentially escalating from limited agent permissions to full human access, or using human permissions for actions the agent shouldn't perform.

The primary mitigation is short-lived merged identities. If the composite token expires in 15 minutes, compromise windows are limited. However, this requires efficient token refresh mechanisms so legitimate agents aren't constantly interrupted.

Audit logging becomes critical for attribution. Without clear logs showing "Agent X acting as Human Y performed action Z", investigations become impossible. The logs must distinguish: agent actions with native identity, agent actions with delegated identity, and direct human actions.

Compliance frameworks care deeply about this. HIPAA's PHI access tracking requires knowing exactly who (human) authorized what (agent action) on which PHI. SOC2's audit controls require demonstrating proper access controls and logging. Merged identities complicate this—systems must track the delegation chain and record both identities.

The refresh token rotation requirement creates challenges for long-running agents. If an agent executes a multi-hour workflow on behalf of a human, the merged identity must refresh multiple times. Each refresh creates a potential failure point and requires re-validation that the delegation is still authorized.

**Implications for Vault Feature**:

Vault's implementation must:

1. **Short-Lived Composite Tokens**: Default 15-30 minute TTL, configurable shorter but not longer
2. **Refresh Mechanism**: Agents can refresh merged identity if:
   - Human session still valid
   - Agent still authorized
   - Delegation policy allows (e.g., max delegation window)
3. **Enhanced Audit Logging**: Every action logs:
   - Entity ID (agent)
   - Delegation context (human identity, delegation start time, JWT ID)
   - Action (what was done)
   - Result (success/failure)
   - Timestamp
4. **Revocation**: Support revoking:
   - All delegations to a specific agent
   - All delegations from a specific human
   - A specific delegation (by composite token's jti)
5. **Policy Composition**: Explicitly define how human and agent policies combine:
   - Intersection (most restrictive)
   - Union (least restrictive)
   - Human-restricted (agent can only access subset of human's permissions)
   - Policy-defined (explicit rules in delegation policy)
6. **Compliance Reporting**: API endpoints for:
   - List all active delegations
   - Audit trail of delegation creation/use/expiration
   - Report on delegation patterns (for anomaly detection)

### Question 5: How do other systems implement hybrid human-agent identity?

**Summary**: AWS, Azure, and GCP all implement hybrid identity through token exchange and role assumption mechanisms, with consistent patterns of trust establishment, short-lived credentials, and attribute-based access control.

**Key Findings**:

**AWS IAM** (Sources: #7, #8):
- Role assumption via `sts:AssumeRole` with trust policies defining who can assume
- Session tags pass context during assumption (evaluated as `aws:PrincipalTag/TagKey`)
- Transitive tags persist through role chaining
- `sts:TagSession` permission required in trust policy
- AWS services (EC2, ECS, EKS, Lambda) auto-rotate credentials

**Azure** (Source: #9):
- Workload identity federation on user-assigned managed identities
- Federated credentials trust external IdP tokens (matching issuer + subject)
- Supports Kubernetes, GitHub Actions, GitLab, any OIDC IdP
- Max 20 federated credentials per identity
- Eliminates secret management entirely
- Recommended audience: "api://AzureADTokenExchange"

**GCP** (Sources: #10, #11):
- Workload identity federation follows OAuth 2.0 token exchange
- Two-stage: External token → federated token → service account impersonation
- IAM bindings reference external identity by subject/group/attributes
- Service account impersonation produces 1-hour access tokens
- Supports X.509, AWS, Azure, OIDC, SAML IdPs

**SPIFFE/SPIRE** (Source: #5):
- SPIFFE IDs: URIs like `spiffe://trust-domain/workload-path`
- X.509-SVID (preferred) and JWT-SVID
- Automatic workload attestation without pre-shared secrets
- Frequent automatic key rotation
- Trust bundles for cross-workload verification

**Convergence Patterns**:

All implementations share:
1. Trust establishment (OIDC/SAML/X.509)
2. Token exchange (OAuth 2.0 or similar)
3. Short-lived credentials (1 hour typical)
4. Attribute-based binding (subject, group, custom attributes)
5. No long-lived secrets in applications

**Analysis**:

The cloud provider convergence validates that token exchange is the right pattern. Despite different APIs and terminology, all three major providers implement essentially the same flow: establish trust with external IdP, exchange external token for internal credentials, use attributes from external token for access control decisions, issue short-lived internal credentials.

AWS's session tags are unique in making context explicit and transitive. This is powerful for delegation chains—each hop can add context, and subsequent hops can make decisions based on accumulated context. For AI agents, this means the agent could add metadata (workflow ID, step number) to the human's context.

Azure's 20 credential limit is interesting—it suggests that unbounded federation can create management overhead. For Vault, this suggests limits on how many humans can delegate to a single agent simultaneously, or how many agents a human can delegate to.

GCP's two-stage process (federation → impersonation) provides a security boundary. The federated token proves external identity; impersonation is a separate decision. This allows different policies: "This external identity is trusted" vs. "This identity can impersonate this service account". For Vault, this suggests separating "Human JWT is valid" from "Human JWT can delegate to this agent".

SPIFFE/SPIRE's automatic attestation is compelling for native workloads. However, for AI agents running in diverse environments (cloud functions, containers, on-prem), attestation is harder. Vault's approach might hybrid: SPIFFE attestation where possible, JWT auth where necessary.

**Implications for Vault Feature**:

Vault should adopt GCP's two-stage pattern:

**Stage 1: Human JWT Validation**
- Vault validates human JWT against trusted IdP (OIDC discovery)
- Extracts claims (sub, email, groups, etc.)
- Creates or updates entity alias for the human

**Stage 2: Agent Delegation Authorization**
- Policy evaluates: Can this human delegate to this agent?
- Checks might include:
  - Human's groups or roles
  - Agent's metadata (approved for delegation)
  - Time of day / location (zero trust policies)
  - Previous delegation history (rate limiting)
- If approved, create composite token with:
  - Agent entity as primary
  - Human identity in actor claim
  - Combined metadata
  - Short TTL

Vault could support session metadata similar to AWS session tags, allowing agents to attach workflow context that propagates through service chains.

### Question 6: What are the specific challenges for AI agent identity in LangGraph and similar frameworks?

**Summary**: AI agents require Just-In-Time authorization with human-in-the-loop patterns, dynamic tool authorization, comprehensive audit trails for compliance, and integration with frameworks' authentication handlers.

**Key Findings**:

**LangGraph Authentication Model** (Sources: #20, #21):
- `@auth.authenticate`: Verifies identity, returns user context
- `@auth.on`: Authorizes specific actions
- User identity available via `config["configuration"]["langgraph_auth_user"]`
- Custom authentication enables delegated access with user-scoped credentials

**Human-in-the-Loop** (Sources: #20, #21):
- Built-in statefulness: agents draft, humans approve
- Breakpoints: interrupt agent sequences for human decision
- CIBA (Client-Initiated Backchannel Authentication): asynchronous authorization without browser redirects
- Maintains agent efficiency while keeping humans in control

**Authorization Best Practices** (Sources: #22, #23, #24):
- OAuth-based with Just-In-Time, least-privileged access
- Dynamic tool authorization: agents request OAuth only when tools are needed
- Avoid upfront pre-authorization of all services
- Four-perimeter security:
  1. Prompt protection (verify user identity)
  2. Secure document retrieval (access control on vector stores)
  3. External action controls (prevent unauthorized operations)
  4. Response enforcement (prevent data leaks)

**Production Requirements** (Sources: #23, #24):
- Limit permissions to application needs
- Read-only credentials where possible
- Credential management mechanisms (not long-lived secrets)
- Authentication flows: Auth Code Flow, On-Behalf-Of, Client Credentials
- Just-In-Time security: grant minimum privilege only when needed, revoke immediately

**Analysis**:

AI agents present unique challenges because they operate autonomously over extended periods, make complex decisions, and interact with multiple services. Traditional IAM assumes either: (1) human user making interactive decisions, or (2) service account with static permissions. AI agents are neither—they're autonomous but should act on human authority.

The human-in-the-loop requirement reflects that agents aren't fully trusted. Humans establish intent (research this topic, write this document, analyze this data), but agents determine steps. Breakpoints provide human oversight at critical decision points: "I'm about to delete these records, approve?" This requires identity context: the approval must come from the human who delegated to the agent, not any human.

Dynamic tool authorization addresses the impracticality of pre-authorizing agents for all possible tools. An agent writing a document might need GitHub, Slack, Google Docs, Notion—but which ones depends on runtime decisions. Pre-authorizing all requires excessive permissions; dynamic authorization requests OAuth only for tools actually used, matching least privilege.

CIBA enables asynchronous authorization, crucial for long-running workflows. An agent starts a task, encounters a decision requiring approval, sends CIBA request to human, continues other work, and resumes when approval arrives. This wouldn't work with traditional browser redirects.

The four-perimeter security model recognizes AI-specific risks: prompt injection (attacker-controlled input modifying agent behavior), data leaks (LLMs may include training data in responses), unauthorized actions (agents calling APIs they shouldn't), and inadequate access controls (vector stores containing sensitive data without proper restrictions).

For compliance, the challenge is attribution. HIPAA requires knowing exactly who accessed PHI. If an agent accesses PHI, is that the human's responsibility? The agent developer's? The agent itself? Delegation semantics answer this: the agent accessed PHI on behalf of the human, so both are logged, but the human bears responsibility for delegating to an appropriate agent.

**Implications for Vault Feature**:

Vault's Langgraph integration must:

1. **Authentication Handler Integration**:
   - Provide SDK for LangGraph's `@auth.authenticate`
   - SDK gets composite token from Vault (human JWT + agent identity)
   - Returns user context: human identity, agent identity, permissions, delegation metadata

2. **Dynamic Tool Authorization**:
   - Agents request Vault credentials for specific tools just-in-time
   - Vault checks: Is tool within delegated scope? Has human pre-approved this tool class?
   - Issue short-lived credentials (15 minutes) for that tool
   - Revoke automatically when agent confirms completion

3. **Human-in-the-Loop Support**:
   - CIBA integration: agent requests approval, Vault sends CIBA challenge to human's device
   - Breakpoint credentials: agent gets limited credentials, requests elevated credentials at breakpoint, human approves, Vault issues elevated credentials for next phase
   - Approval history: log all approvals with context for audit

4. **Comprehensive Audit Logging**:
   - Every agent action logs: agent ID, human ID, delegation ID, action, result, timestamp
   - Tool authorization logs: which tools requested, which approved, which denied
   - Approval logs: what was requested, what was approved, by whom, when

5. **Four-Perimeter Controls**:
   - Prompt protection: validate human identity before accepting delegation
   - Secure document retrieval: Vault policies restrict agent access to vector stores based on human's data access permissions
   - External action controls: explicit allow-listing of tools/APIs agents can access
   - Response enforcement: Vault doesn't control LLM output, but policies can restrict which data sources agent can query

6. **Framework Integration Examples**:
   - LangGraph: `@auth.authenticate` implementation
   - LangChain: Custom authentication handler
   - CrewAI: Authentication provider plugin
   - Autogen: Integration with authentication framework

This creates a comprehensive solution where Vault becomes the identity and authorization layer for AI agents, handling delegation, dynamic authorization, human-in-the-loop, and compliance logging.

---

## Recommended Architecture for Vault Feature

Based on comprehensive research findings, the optimal architecture for merging human JWT identity with Vault agent identity follows these principles:

### 1. Entity-Based Foundation

Leverage Vault's existing entity system:
- **Agent Entity**: Represents the agent's native identity (created via AppRole, JWT, or other auth method)
- **Composite Entity Alias**: New alias type representing human-delegated access
- **Policy Inheritance**: Entity-level policies define base agent permissions; alias-level policies add human-delegated permissions

### 2. OAuth 2.0 Token Exchange Pattern

Follow RFC 8693 standard:
- **Subject Token**: Human JWT from external IdP (Auth0, Okta, Azure AD, etc.)
- **Security Token Service**: Vault acts as STS, validating human JWT and issuing composite token
- **Actor Claim**: Resulting JWT includes `"act"` claim with agent identity
- **Grant Type**: `urn:ietf:params:oauth:grant-type:token-exchange`

### 3. Two-Stage Authorization

Separate validation from delegation (GCP pattern):

**Stage 1 - Human JWT Validation:**
- Verify JWT signature against IdP's JWKS
- Validate claims: iss, aud, exp, nbf
- Ensure human is authenticated and session valid
- Extract human identity attributes (sub, email, groups, roles)

**Stage 2 - Delegation Authorization:**
- Evaluate policy: Can this human delegate to this agent?
- Check conditions:
  - Human's authorization level (admin, user, etc.)
  - Agent's delegation eligibility (approved agents only)
  - Time/location constraints (zero trust policies)
  - Rate limits (prevent abuse)
- If approved, create composite entity alias and issue composite token

### 4. Composite Token Structure

JWT format for merged identity:
```json
{
  "iss": "https://vault.example.com",
  "sub": "agent-abc-123",
  "act": {
    "sub": "human-xyz-789",
    "email": "user@example.com",
    "groups": ["engineering", "security"],
    "iss": "https://auth0.example.com"
  },
  "aud": ["api.example.com"],
  "exp": 1704384000,
  "iat": 1704382200,
  "nbf": 1704382200,
  "jti": "unique-token-id-456",
  "scope": "read:secrets write:logs access:database",
  "delegation": {
    "delegated_at": 1704382200,
    "delegation_id": "del-unique-id",
    "human_jwt_jti": "original-human-jwt-id"
  }
}
```

### 5. Policy Composition

Explicit rules for combining permissions:

**Intersection Model** (most secure, default):
```hcl
path "secret/data/*" {
  capabilities = ["read"]

  # Agent has read permission AND human has read permission
  required_capabilities = {
    entity = ["read"],
    delegation = ["read"]
  }
}
```

**Human-Restricted Model** (agent subset of human):
```hcl
path "secret/data/sensitive/*" {
  # Agent can only access if human explicitly has access
  # Agent's native permissions don't apply to sensitive paths
  allowed_entity_aliases = ["composite"]
  required_delegation_permission = true
}
```

**Union Model** (least secure, opt-in only):
```hcl
path "logs/write/*" {
  # Agent can write logs with either native OR delegated permission
  allowed_either = {
    entity = ["write"],
    delegation = ["write"]
  }
}
```

### 6. Lifecycle Management

**Creation:**
1. Agent authenticates with native method (AppRole, JWT) → gets agent token
2. Agent calls `/v1/auth/delegation/create` with:
   - Agent token (in header)
   - Human JWT (in body)
   - Requested scope (optional, defaults to agent's scope)
3. Vault validates both, applies delegation policy, creates composite alias
4. Returns composite token with short TTL (15-30 min)

**Refresh:**
1. Agent calls `/v1/auth/delegation/refresh` with:
   - Composite token (in header)
   - Human session still valid (Vault checks IdP)
   - Delegation still authorized (policy evaluation)
2. Vault issues new composite token, rotates jti, updates delegation metadata

**Revocation:**
- `/v1/auth/delegation/revoke` - revoke specific delegation by ID
- `/v1/auth/delegation/revoke-agent/{entity-id}` - revoke all delegations to this agent
- `/v1/auth/delegation/revoke-human/{human-sub}` - revoke all delegations from this human
- Automatic revocation when human JWT expires or session invalidates

### 7. Audit Logging

Enhanced audit events:
```json
{
  "type": "delegation_created",
  "timestamp": "2025-01-03T12:00:00Z",
  "entity_id": "agent-abc-123",
  "human": {
    "sub": "human-xyz-789",
    "iss": "https://auth0.example.com",
    "email": "user@example.com"
  },
  "delegation_id": "del-unique-id",
  "requested_scope": "read:secrets write:logs",
  "granted_scope": "read:secrets",
  "ttl": 1800,
  "policy_evaluation": "approved"
}

{
  "type": "request",
  "timestamp": "2025-01-03T12:05:00Z",
  "path": "secret/data/database/credentials",
  "operation": "read",
  "entity_id": "agent-abc-123",
  "delegation_id": "del-unique-id",
  "delegation": {
    "human_sub": "human-xyz-789",
    "human_email": "user@example.com"
  },
  "result": "success"
}
```

### 8. LangGraph Integration

SDK for seamless integration:

**Python SDK:**
```python
from vault_agent_auth import VaultDelegationAuth

# Initialize with Vault address and agent credentials
auth = VaultDelegationAuth(
    vault_addr="https://vault.example.com",
    agent_role_id="agent-role-id",
    agent_secret_id="agent-secret"
)

# LangGraph authentication handler
@auth.authenticate
async def authenticate_with_delegation(request):
    # Extract human JWT from request (e.g., Authorization header)
    human_jwt = request.headers["Authorization"].replace("Bearer ", "")

    # Get composite token from Vault
    composite_token = await auth.create_delegation(human_jwt)

    # Return user context for LangGraph
    return {
        "langgraph_auth_user": composite_token.human_email,
        "vault_token": composite_token.token,
        "agent_id": composite_token.agent_id,
        "permissions": composite_token.scope
    }

# Use in LangGraph agent
config = {
    "configuration": {
        "langgraph_auth_user": context["langgraph_auth_user"],
        "vault_token": context["vault_token"]
    }
}
```

**Just-In-Time Tool Authorization:**
```python
# Agent needs to access GitHub API
async def authorize_tool(tool_name: str, context: dict):
    vault_token = context["vault_token"]

    # Request just-in-time credentials from Vault
    tool_creds = await auth.get_tool_credentials(
        vault_token=vault_token,
        tool=tool_name,
        ttl=900  # 15 minutes
    )

    return tool_creds

# In agent code
github_creds = await authorize_tool("github", context)
github_client = GitHubClient(token=github_creds.token)
```

### 9. Compliance Support

**SOC2 / HIPAA Audit APIs:**
```bash
# List all active delegations
curl -H "X-Vault-Token: $TOKEN" \
  https://vault.example.com/v1/auth/delegation/list

# Get delegation audit trail
curl -H "X-Vault-Token: $TOKEN" \
  https://vault.example.com/v1/auth/delegation/audit?delegation_id=del-123

# Report on human's delegations (for compliance review)
curl -H "X-Vault-Token: $TOKEN" \
  https://vault.example.com/v1/auth/delegation/report/human/human-xyz-789

# Report on agent's delegations (for security review)
curl -H "X-Vault-Token: $TOKEN" \
  https://vault.example.com/v1/auth/delegation/report/agent/agent-abc-123
```

### 10. Security Boundaries

**Rate Limiting:**
- Max 100 active delegations per human
- Max 10 delegations per agent simultaneously
- Max 1000 delegation creations per human per day

**Scope Restrictions:**
- Composite tokens cannot have broader scope than agent's native permissions
- Delegation policy can further restrict scope
- Sensitive paths require explicit delegation authorization

**Time Boundaries:**
- Default TTL: 30 minutes
- Maximum TTL: 4 hours (configurable)
- Refresh allowed only if human session valid and within maximum delegation window (default 24 hours)

**Revocation Guarantees:**
- Revoked delegations invalid within 5 seconds globally
- Human JWT expiration causes automatic revocation check on next refresh
- IdP session invalidation causes revocation on next Vault-to-IdP validation

---

## Sources Consulted

### Academic & Industry Reports
1. AppViewX - 2024 ESG Report on NHI Management
2. GitGuardian/OWASP - OWASP Top 10 Non-Human Identity Risks for 2025
3. Verizon - 2025 DBIR

### Standards & Specifications
4. IETF RFC 8693 - OAuth 2.0 Token Exchange
5. SPIFFE.io - SPIFFE Concepts Documentation
6. W3C - Trace Context Standard

### Cloud Provider Documentation
7. AWS Security Blog - IAM Trust Policies
8. AWS IAM - Session Tags Documentation
9. Microsoft Learn - Azure Managed Identity Workload Federation
10. Google Cloud - Workload Identity Federation
11. Google Cloud IAM - Service Account Impersonation

### HashiCorp Vault Resources
12. HashiCorp Developer - Vault JWT/OIDC Authentication
13. HashiCorp Developer - Vault Identity Entities and Groups
14. HashiCorp GitHub - vault-plugin-auth-jwt

### Security & Token Management
15. Hoop.dev - JWT Privilege Escalation Insights
16. Serverion - Refresh Token Rotation Best Practices
17. OWASP - JWT Security Best Practices Cheat Sheet
18. Scott Brady (IdentityServer) - OAuth 2.0 Delegation Patterns
19. Curity.io - Token Exchange and Impersonation Flows

### AI Agent Security & Identity
20. LangChain - LangGraph Authentication & Access Control
21. Auth0 Blog - Human-in-the-Loop Authorization with LangGraph
22. Arcade.dev - Agent Auth: Production Agents Problem
23. LangChain - Security Best Practices
24. LangChain Blog - Agent Authorization Explainer

### Compliance & Audit
25. Secureframe - SOC 2 + HIPAA Compliance Guide
26. ISpartners - SOC 2 vs HIPAA Comparative Review

### Microservices & Distributed Systems
27. Google Cloud Blog - Identity Propagation in API Gateway
28. Microservices.io - Audit Logging Pattern
29. SigNoz - Context Propagation in Distributed Tracing
30. Nordic APIs - Identity and Access Management in Microservices

### Best Practices & Implementation Guides
31. NHIMG.org - Service Account Management Strategies for 2025
32. NHIMG.org - Ultimate Guide to Non-Human Identities
33. NHIMG.org - Identity Lifecycle Management for NHI
34. Permit.io - Four-Perimeter Access Control in LangChain

---

## Conclusion

Merging human JWT identity with Vault agent identity requires careful architectural design balancing security, usability, and compliance. The recommended approach leverages Vault's existing entity system with OAuth 2.0 token exchange patterns, creating composite identities that maintain clear attribution through delegation semantics. By following industry best practices from cloud providers, implementing short-lived credentials with automatic rotation, and providing comprehensive audit logging, the solution enables AI agentic frameworks like LangGraph to operate securely on behalf of users while meeting SOC2 and HIPAA compliance requirements.

The implementation priority should focus on: (1) core delegation API with composite token issuance, (2) policy composition engine, (3) comprehensive audit logging, (4) LangGraph SDK and integration examples, (5) compliance reporting APIs. This phased approach allows iterative development with early validation from LangGraph users, refinement based on real-world usage patterns, and expansion to additional frameworks (LangChain, CrewAI, Autogen) once the core pattern is proven.

---

**Document Status**: Final Research Report
**Next Steps**: Architecture design, POC implementation, security review, LangGraph integration testing