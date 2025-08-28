from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class PolicyDecisionResult(str, Enum):
    """Policy decision result enumeration"""
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class RegisterAgentOptions:
    """Options for registering a new agent"""
    agent_name: str
    capabilities: List[str]
    developer_did: Optional[str] = None

@dataclass
class AuthAssertionParams:
    """Parameters for agent authentication assertion"""
    agent_did: str
    vc: str  # Verifiable Credential for this agent
    audience: str  # e.g. https://api.identitymachines.com
    developer_did: Optional[str] = None

@dataclass
class GetAuthTokenOptions:
    """Options for getting authentication token"""
    agent_did: str
    vc: str
    action: str
    resource: str
    audience: str
    developer_did: Optional[str] = None

@dataclass
class PolicyInput:
    """Input parameters for policy decision"""
    agent_did: str  # agent DID (subject)
    policy_id: str  # specific policy ID to use
    token: str  # short-lived access token (JWT)
    context: Optional[Dict[str, Any]] = None  # optional: amount, ticker, etc.

@dataclass
class PolicyDecision:
    """Result of a policy decision"""
    allow: bool
    evaluation: Optional[List[Any]] = None
    reason: Optional[str] = None

@dataclass
class BuildAgentPayloadOptions:
    """Options for building agent payload"""
    agent_name: str
    capabilities: List[str]
    developer_did: str  # DID identifying the agent's owner/issuer

@dataclass
class AgentPayload:
    """Structure sent to Iron Book API and returned to caller"""
    agent_did: str  # did:web:...
    developer_did: str  # did:web:...
    vc: str  # detached JWS VC (compact)
    public_jwk: Dict[str, Any]  # to persist in agent registry for auth token verification
    private_jwk: Dict[str, Any]  # returned for caller to securely store

@dataclass
class UploadPolicyOptions:
    """Options for uploading a policy"""
    config_type: str
    policy_content: str
    metadata: Any
    developer_did: Optional[str] = None

@dataclass
class UpdateAgentOptions:
    """Options for updating an agent"""
    description: Optional[str] = None
    status: Optional[str] = None  # 'active' or 'inactive'

@dataclass
class UpdateAgentResponse:
    """Response from updating an agent"""
    agent_did: str
    developer_did: str
    updated: List[str]  # List of updated field names


# ===============================
# Agent retrieval/listing types
# ===============================

@dataclass
class AgentResponse:
    """Agent record returned by the API (sanitized, no keys)"""
    did: str
    name: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    trust_score: Optional[float] = None
    status: Optional[str] = None  # 'active' | 'inactive'
    vc: Optional[str] = None
    org_id: Optional[str] = None
    developer_did: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ListAgentsOptions:
    """Options for listing agents"""
    status: Optional[str] = None  # 'active' | 'inactive'
    capabilities: Optional[List[str]] = None  # All must match
    limit: Optional[int] = None  # 1-100; default 25
    last_key: Optional[str] = None  # Opaque cursor


@dataclass
class ListAgentsResponse:
    """Response from listing agents"""
    items: List[AgentResponse]
    count: int
    last_key: Optional[str] = None

# ===============================
# Policy get/list types
# ===============================

@dataclass
class Policy:
    agent_did: str
    policy_id: Optional[str] = None
    policy_content: Optional[str] = None
    developer_did: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[Any] = None

@dataclass
class ListPoliciesResponse:
    items: List[Policy]
    count: int
    last_key: Optional[str] = None

@dataclass
class ListPoliciesOptions:
    is_active: Optional[bool] = None
    limit: Optional[int] = None
    last_key: Optional[str] = None

# ===============================
# Audit log listing types
# ===============================

@dataclass
class ListAuditLogsOptions:
    agent_did: Optional[str] = None
    event_type: Optional[str] = None  # REGISTER | AUTH | POLICY | UPDATE
    policy_id: Optional[str] = None
    allow: Optional[bool] = None
    since: Optional[str] = None  # ISO 8601 start
    until: Optional[str] = None  # ISO 8601 end
    limit: Optional[int] = None
    last_key: Optional[str] = None

@dataclass
class ListAuditLogsResponse:
    items: List['AuditLogEntry']
    count: int
    last_key: Optional[str] = None

@dataclass
class AuditLogEntry:
    agent_did: str
    event_type: str  # REGISTER | AUTH | POLICY | UPDATE
    timestamp: str
    trust_score: float
    delta: float
    policy_id: Optional[str] = None
    action: Optional[str] = None
    resource: Optional[str] = None
    allow: Optional[bool] = None
    input: Optional[Dict[str, Any]] = None
    details: Optional[str] = None

# Type aliases for backward compatibility and convenience
RegisterAgentOptions = RegisterAgentOptions
GetAuthTokenOptions = GetAuthTokenOptions
PolicyDecision = PolicyDecision