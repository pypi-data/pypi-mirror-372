import pytest
import httpx
import json
from unittest.mock import AsyncMock, patch
from ironbook_sdk.client import IronBookClient, IronBookError
from ironbook_sdk.types import UpdateAgentOptions, UpdateAgentResponse

@pytest.fixture
def client():
    return IronBookClient("test-api-key", "https://test.example.com")

@pytest.fixture
def mock_response():
    return {
        "agentDid": "did:web:agents.identitymachines.com:testagent",
        "developerDid": "did:web:identitymachines.com",
        "updated": ["description", "status"]
    }

class TestUpdateAgent:
    """Test cases for the update_agent method"""

    @pytest.mark.asyncio
    async def test_update_agent_description_only(self, client, mock_response):
        """Test updating only the description"""
        with patch.object(client.client, 'put') as mock_put:
            mock_put.return_value = AsyncMock(
                is_success=True,
                json=lambda: mock_response
            )

            opts = UpdateAgentOptions(description="Updated description")
            result = await client.update_agent("did:web:agents.identitymachines.com:testagent", opts)

            assert isinstance(result, UpdateAgentResponse)
            assert result.agent_did == "did:web:agents.identitymachines.com:testagent"
            assert result.developer_did == "did:web:identitymachines.com"
            assert result.updated == ["description", "status"]

            # Verify the request
            mock_put.assert_called_once_with(
                "https://test.example.com/agents/did:web:agents.identitymachines.com:testagent",
                headers={
                    'Content-Type': 'application/json',
                    'x-ironbook-key': 'test-api-key'
                },
                json={"description": "Updated description"}
            )

    @pytest.mark.asyncio
    async def test_update_agent_status_only(self, client, mock_response):
        """Test updating only the status"""
        with patch.object(client.client, 'put') as mock_put:
            mock_put.return_value = AsyncMock(
                is_success=True,
                json=lambda: mock_response
            )

            opts = UpdateAgentOptions(status="inactive")
            result = await client.update_agent("did:web:agents.identitymachines.com:testagent", opts)

            assert isinstance(result, UpdateAgentResponse)
            assert result.agent_did == "did:web:agents.identitymachines.com:testagent"

            # Verify the request
            mock_put.assert_called_once_with(
                "https://test.example.com/agents/did:web:agents.identitymachines.com:testagent",
                headers={
                    'Content-Type': 'application/json',
                    'x-ironbook-key': 'test-api-key'
                },
                json={"status": "inactive"}
            )

    @pytest.mark.asyncio
    async def test_update_agent_both_fields(self, client, mock_response):
        """Test updating both description and status"""
        with patch.object(client.client, 'put') as mock_put:
            mock_put.return_value = AsyncMock(
                is_success=True,
                json=lambda: mock_response
            )

            opts = UpdateAgentOptions(
                description="Updated description",
                status="active"
            )
            result = await client.update_agent("did:web:agents.identitymachines.com:testagent", opts)

            assert isinstance(result, UpdateAgentResponse)

            # Verify the request
            mock_put.assert_called_once_with(
                "https://test.example.com/agents/did:web:agents.identitymachines.com:testagent",
                headers={
                    'Content-Type': 'application/json',
                    'x-ironbook-key': 'test-api-key'
                },
                json={
                    "description": "Updated description",
                    "status": "active"
                }
            )

    @pytest.mark.asyncio
    async def test_update_agent_no_fields_provided(self, client):
        """Test that an error is raised when no fields are provided"""
        opts = UpdateAgentOptions()
        
        with pytest.raises(IronBookError, match="At least one of description or status must be provided"):
            await client.update_agent("did:web:agents.identitymachines.com:testagent", opts)

    @pytest.mark.asyncio
    async def test_update_agent_http_error(self, client):
        """Test handling of HTTP errors"""
        with patch.object(client.client, 'put') as mock_put:
            mock_put.return_value = AsyncMock(
                is_success=False,
                status_code=404,
                text="Agent not found"
            )

            opts = UpdateAgentOptions(description="Updated description")
            
            with pytest.raises(IronBookError, match="Agent update error \\(404\\): Agent not found"):
                await client.update_agent("did:web:agents.identitymachines.com:testagent", opts)

    @pytest.mark.asyncio
    async def test_update_agent_network_error(self, client):
        """Test handling of network errors"""
        with patch.object(client.client, 'put') as mock_put:
            mock_put.side_effect = httpx.RequestError("Network error")

            opts = UpdateAgentOptions(description="Updated description")
            
            with pytest.raises(IronBookError, match="Network error during agent update"):
                await client.update_agent("did:web:agents.identitymachines.com:testagent", opts)

    @pytest.mark.asyncio
    async def test_update_agent_invalid_json(self, client):
        """Test handling of invalid JSON responses"""
        with patch.object(client.client, 'put') as mock_put:
            mock_response = AsyncMock()
            mock_response.is_success = True
            # Use a regular Mock for the json method since it's not async
            from unittest.mock import Mock
            mock_response.json = Mock(side_effect=json.JSONDecodeError("Expecting value", "invalid json", 0))
            mock_put.return_value = mock_response

            opts = UpdateAgentOptions(description="Updated description")
            
            with pytest.raises(IronBookError, match="Invalid JSON response during agent update"):
                await client.update_agent("did:web:agents.identitymachines.com:testagent", opts)

    @pytest.mark.asyncio
    async def test_update_agent_url_encoding(self, client, mock_response):
        """Test that agent DID is properly URL encoded"""
        with patch.object(client.client, 'put') as mock_put:
            mock_put.return_value = AsyncMock(
                is_success=True,
                json=lambda: mock_response
            )

            opts = UpdateAgentOptions(description="Updated description")
            agent_did = "did:web:agents.identitymachines.com:test:agent"
            
            await client.update_agent(agent_did, opts)

            # Verify the URL encoding
            mock_put.assert_called_once_with(
                "https://test.example.com/agents/did:web:agents.identitymachines.com:test:agent",
                headers={
                    'Content-Type': 'application/json',
                    'x-ironbook-key': 'test-api-key'
                },
                json={"description": "Updated description"}
            )

class TestUpdateAgentConvenienceFunction:
    """Test cases for the convenience update_agent function"""

    @pytest.mark.asyncio
    async def test_convenience_function(self, mock_response):
        """Test the convenience function works correctly"""
        with patch('ironbook_sdk.client.IronBookClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.__aenter__.return_value = mock_client
            mock_client.update_agent.return_value = UpdateAgentResponse(
                agent_did="did:web:agents.identitymachines.com:testagent",
                developer_did="did:web:identitymachines.com",
                updated=["description"]
            )

            from ironbook_sdk.client import update_agent
            
            opts = UpdateAgentOptions(description="Updated description")
            result = await update_agent("did:web:agents.identitymachines.com:testagent", opts, "test-api-key")

            assert isinstance(result, UpdateAgentResponse)
            assert result.agent_did == "did:web:agents.identitymachines.com:testagent"
            assert result.updated == ["description"]

            # Verify the client was used correctly
            mock_client_class.assert_called_once_with("test-api-key", "https://dev.identitymachines.com")
            mock_client.update_agent.assert_called_once_with("did:web:agents.identitymachines.com:testagent", opts)
            mock_client.__aenter__.assert_called_once()
            mock_client.__aexit__.assert_called_once() 