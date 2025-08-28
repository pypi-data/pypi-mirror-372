# ironbook/client.py
import httpx
import json
from typing import Dict, Any, Optional, List
from .types import (
    RegisterAgentOptions, 
    GetAuthTokenOptions, 
    Policy,
    PolicyDecision, 
    PolicyInput,
    UploadPolicyOptions,
    UpdateAgentOptions,
    UpdateAgentResponse,
    AgentResponse,
    ListAgentsOptions,
    ListAgentsResponse,
    ListPoliciesOptions,
    ListPoliciesResponse,
    ListAuditLogsOptions,
    ListAuditLogsResponse,
    AuditLogEntry,
)

class IronBookError(Exception):
    """IronBook SDK error with structured fields."""
    def __init__(self, message: str, *, status: int, code: Optional[str] = None, request_id: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.request_id = request_id
        self.details = details

class IronBookClient:
    """IronBook Trust Service client"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.ironbook.identitymachines.com", timeout: float = 10.0):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'x-ironbook-key': self.api_key
        }

    async def _request(self, method: str, path: str, *, json_body: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        req_headers = self._get_headers()
        if headers:
            req_headers.update(headers)
        try:
            resp = await self.client.request(method, url, headers=req_headers, json=json_body)
            ct = resp.headers.get('content-type', '')
            is_json = 'json' in ct
            if resp.is_success:
                return resp.json() if is_json else { 'data': resp.text }
            # Build structured error
            body: Any = None
            if is_json:
                try:
                    body = resp.json()
                except json.JSONDecodeError:
                    body = None
            else:
                body = resp.text
            title = body.get('title') if isinstance(body, dict) else None
            fallback = (body.get('error') or body.get('message')) if isinstance(body, dict) else None
            code = body.get('code') or body.get('type') if isinstance(body, dict) else None
            request_id = body.get('requestId') if isinstance(body, dict) else None
            message = title or fallback or f"HTTP {resp.status_code}"
            raise IronBookError(message, status=resp.status_code, code=code, request_id=request_id, details=body)
        except httpx.TimeoutException as e:
            raise IronBookError("Request timed out", status=408, code="REQUEST_TIMEOUT") from e
        except httpx.RequestError as e:
            raise IronBookError(f"Network error: {e}", status=0) from e
        except json.JSONDecodeError as e:
            # successful response but not valid JSON
            raise IronBookError(f"Invalid JSON response: {e}", status=200) from e
    
    async def register_agent(self, opts: RegisterAgentOptions) -> Dict[str, Any]:
        """
        Registers a new agent with the Iron Book Trust Service
        
        Args:
            opts: Registration options including agent name, capabilities, and developer DID
            
        Returns:
            Dict[str, Any]: Response containing vc (Verifiable Credential as a compact-format signed JWT string for this agent), agentDid, and developerDid
            
        Raises:
            IronBookError: If registration fails
        """
        payload = {
            'agentName': opts.agent_name,
            'capabilities': opts.capabilities,
            'developerDID': opts.developer_did
        }
        return await self._request('POST', '/agents/register', json_body=payload)
    
    async def get_auth_token(self, opts: GetAuthTokenOptions) -> Dict[str, Any]:
        """
        Gets a short-lived one-shot JIT access token for the agent to perform an action
        
        Args:
            opts: Authentication options including agent DID, developer DID, VC, and audience
            
        Returns:
            Dict[str, Any]: Response containing access_token and expires_in
            
        Raises:
            IronBookError: If authentication fails
        """
        payload = {
            'agentDid': opts.agent_did,
            'developerDid': opts.developer_did,
            'vc': opts.vc,
            'action': opts.action,  # e.g. "query"
            'resource': opts.resource,  # e.g. "db://finance/tx"
            'audience': opts.audience
        }
        return await self._request('POST', '/auth/token', json_body=payload)
    
    async def policy_decision(self, opts: PolicyInput) -> PolicyDecision:
        """
        Gets a policy decision from the Iron Book Trust Service and consumes the one-shot JIT access token
        
        Args:
            opts: Policy decision input including agent DID, token, action, resource, and context
            
        Returns:
            PolicyDecision: Policy decision result with allow/deny and additional details
            
        Raises:
            IronBookError: If policy decision fails
        """
        headers = {'Authorization': f'Bearer {opts.token}'}
        payload = {
            'agentDid': opts.agent_did,  # agent DID
            'policyId': opts.policy_id,   # policy ID
            'context': opts.context or {}  # optional: amount, ticker, etc.
        }
        data = await self._request('POST', '/policy/decision', json_body=payload, headers=headers)
        return PolicyDecision(
            allow=data.get('allow', False),
            evaluation=data.get('evaluation'),
            reason=data.get('reason')
        )

    async def upload_policy(self, opts: UploadPolicyOptions) -> Dict[str, Any]:
        """
        Uploads a new access control policy to the Iron Book Trust Service
        
        Args:
            opts: Policy upload options including developer DID,
                config type, policy content, metadata, and API key
            
        Returns:
            Response from the policy upload endpoint
            
        Raises:
            IronBookError: If the upload fails
        """
        payload = {
            'developerDid': opts.developer_did,
            'configType': opts.config_type,
            'policyContent': opts.policy_content,
            'metadata': opts.metadata
        }
        return await self._request('POST', '/policies', json_body=payload)

    async def update_agent(self, agent_did: str, opts: UpdateAgentOptions) -> UpdateAgentResponse:
        """
        Updates an agent's description and/or status
        
        Args:
            agent_did: The DID of the agent to update
            opts: Update options including description and/or status
            
        Returns:
            UpdateAgentResponse: Response containing agent DID, developer DID, and updated fields
            
        Raises:
            IronBookError: If update fails
        """
        # Build request body with only provided fields
        request_body: Dict[str, Any] = {}
        if opts.description is not None:
            request_body['description'] = opts.description
        if opts.status is not None:
            request_body['status'] = opts.status
        if not request_body:
            raise IronBookError("At least one of description or status must be provided", status=400, code="VALIDATION_ERROR")

        data = await self._request('PUT', f"/agents/{agent_did}", json_body=request_body)
        return UpdateAgentResponse(
            agent_did=data.get('agentDid'),
            developer_did=data.get('developerDid'),
            updated=data.get('updated', [])
        )

    async def get_agent(self, agent_did: str) -> AgentResponse:
        """Retrieve a single agent by DID"""
        data = await self._request('GET', f"/agents/{agent_did}")
        # Map keys from camelCase to snake_case where present
        return AgentResponse(
            did=data.get('did'),
            name=data.get('name'),
            description=data.get('description'),
            capabilities=data.get('capabilities'),
            trust_score=data.get('trustScore'),
            status=data.get('status'),
            vc=data.get('vc'),
            org_id=data.get('orgID'),
            developer_did=data.get('developerDID'),
            created_at=data.get('createdAt'),
            updated_at=data.get('updatedAt'),
        )

    async def list_agents(self, opts: Optional[ListAgentsOptions] = None) -> ListAgentsResponse:
        """List agents with optional filters and pagination"""
        opts = opts or ListAgentsOptions()
        params: List[str] = []
        if opts.status:
            params.append(f"status={opts.status}")
        if opts.capabilities:
            caps = ','.join(opts.capabilities)
            params.append(f"capabilities={caps}")
        if isinstance(opts.limit, int):
            params.append(f"limit={opts.limit}")
        if opts.last_key:
            params.append(f"lastKey={opts.last_key}")
        qs = ('?' + '&'.join(params)) if params else ''
        data = await self._request('GET', f"/agents{qs}")
        items = [
            AgentResponse(
                did=a.get('did'),
                name=a.get('name'),
                description=a.get('description'),
                capabilities=a.get('capabilities'),
                trust_score=a.get('trustScore'),
                status=a.get('status'),
                vc=a.get('vc'),
                org_id=a.get('orgID'),
                developer_did=a.get('developerDID'),
                created_at=a.get('createdAt'),
                updated_at=a.get('updatedAt'),
            ) for a in data.get('items', [])
        ]
        return ListAgentsResponse(
            items=items,
            count=data.get('count', len(items)),
            last_key=data.get('lastKey')
        )

    async def get_policy(self, policy_id: str) -> Policy:
        """Retrieve a single policy by policyId"""
        data = await self._request('GET', f"/policies/{policy_id}")
        return Policy(
            agent_did=data.get('agentDid'),
            policy_id=data.get('policyId'),
            policy_content=data.get('policyContent'),
            developer_did=data.get('developerDID'),
            created_at=data.get('createdAt'),
        )

    async def list_policies(self, opts: Optional[ListPoliciesOptions] = None) -> ListPoliciesResponse:
        """List policies with optional filters and pagination"""
        opts = opts or ListPoliciesOptions()
        params: List[str] = []
        if isinstance(opts.is_active, bool):
            params.append(f"isActive={'true' if opts.is_active else 'false'}")
        if isinstance(opts.limit, int):
            params.append(f"limit={opts.limit}")
        if opts.last_key:
            params.append(f"lastKey={opts.last_key}")
        qs = ('?' + '&'.join(params)) if params else ''
        data = await self._request('GET', f"/policies{qs}")
        items = [
            Policy(
                agent_did=p.get('agentDid'),
                policy_id=p.get('policyId'),
                policy_content=p.get('policyContent'),
                developer_did=p.get('developerDID'),
                created_at=p.get('createdAt'),
            ) for p in data.get('items', [])
        ]
        return ListPoliciesResponse(
            items=items,
            count=data.get('count', len(items)),
            last_key=data.get('lastKey')
        )

    async def list_audit_logs(self, opts: Optional[ListAuditLogsOptions] = None) -> ListAuditLogsResponse:
        """List audit logs with optional filters and pagination"""
        opts = opts or ListAuditLogsOptions()
        params: List[str] = []
        if opts.agent_did:
            params.append(f"agentDid={opts.agent_did}")
        if opts.event_type:
            params.append(f"eventType={opts.event_type}")
        if opts.policy_id:
            params.append(f"policyId={opts.policy_id}")
        if isinstance(opts.allow, bool):
            params.append(f"allow={'true' if opts.allow else 'false'}")
        if opts.since:
            params.append(f"from={opts.since}")
        if opts.until:
            params.append(f"to={opts.until}")
        if isinstance(opts.limit, int):
            params.append(f"limit={opts.limit}")
        if opts.last_key:
            params.append(f"lastKey={opts.last_key}")
        qs = ('?' + '&'.join(params)) if params else ''
        data = await self._request('GET', f"/audit-logs{qs}")
        items = [
            AuditLogEntry(
                agent_did=a.get('agentDid'),
                event_type=a.get('eventType'),
                timestamp=a.get('timestamp'),
                trust_score=a.get('trustScore'),
                delta=a.get('delta'),
                policy_id=a.get('policyId'),
                action=a.get('action'),
                resource=a.get('resource'),
                allow=a.get('allow'),
                input=a.get('input'),
                details=a.get('details'),
            ) for a in data.get('items', [])
        ]
        return ListAuditLogsResponse(items=items, count=data.get('count', 0), last_key=data.get('lastKey'))

# Convenience functions for backward compatibility and simpler usage
async def register_agent(opts: RegisterAgentOptions, api_key: str, base_url: str = "https://api.ironbook.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for registering an agent"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.register_agent(opts)

async def get_auth_token(opts: GetAuthTokenOptions, api_key: str, base_url: str = "https://api.ironbook.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for getting one-shot JIT authentication token"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.get_auth_token(opts)

async def policy_decision(opts: PolicyInput, api_key: str, base_url: str = "https://api.ironbook.identitymachines.com") -> PolicyDecision:
    """Convenience function for getting policy decision"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.policy_decision(opts)

async def upload_policy(opts: UploadPolicyOptions, api_key: str, base_url: str = "https://api.ironbook.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for uploading a new policy"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.upload_policy(opts)

async def update_agent(agent_did: str, opts: UpdateAgentOptions, api_key: str, base_url: str = "https://api.ironbook.identitymachines.com") -> UpdateAgentResponse:
    """Convenience function for updating an agent"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.update_agent(agent_did, opts)

async def get_agent(agent_did: str, api_key: str, base_url: str = "https://api.ironbook.identitymachines.com") -> AgentResponse:
    """Convenience function for retrieving an agent by DID"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.get_agent(agent_did)

async def list_agents(opts: Optional[ListAgentsOptions], api_key: str, base_url: str = "https://api.ironbook.identitymachines.com") -> ListAgentsResponse:
    """Convenience function for listing agents with optional filters"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.list_agents(opts)

async def get_policy(policy_id: str, api_key: str, base_url: str = "https://api.ironbook.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for retrieving a single policy"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.get_policy(policy_id)

async def list_policies(opts: Optional[ListPoliciesOptions], api_key: str, base_url: str = "https://api.ironbook.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for listing policies"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.list_policies(opts)

async def list_audit_logs(opts: Optional[ListAuditLogsOptions], api_key: str, base_url: str = "https://api.ironbook.identitymachines.com") -> ListAuditLogsResponse:
    """Convenience function for listing audit logs"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.list_audit_logs(opts)