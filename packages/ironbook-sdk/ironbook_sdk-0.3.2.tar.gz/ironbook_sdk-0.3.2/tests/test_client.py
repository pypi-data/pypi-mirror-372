import asyncio
import pytest
from ironbook_sdk.client import (
    register_agent,
    get_auth_token,
    upload_policy,
    policy_decision,
    RegisterAgentOptions,
    GetAuthTokenOptions,
    UploadPolicyOptions,
    PolicyInput,
    IronBookError
)

API_KEY = 'ironbook-api-a4f19d3b72e08c5fa1c367d0bb2c6a9e'
AGENT_NAME = 'python-test-agent'
CAPABILITIES = ['read', 'write', 'goof_around']
DEVELOPER_DID = None  # defaults to 'did:web:identitymachines.com'

POLICY_CONTENT = '''
package policies

default allow = false

allow if {
  input.action == "read"
  input.resource == "user-data"
}

allow if {
  input.action == "goof_around"
}

allow if {
  input.action == "write"
  input.resource == "user-data"
  input.context.user == "admin"
}
'''

@pytest.mark.asyncio
async def test_agent_operations():
    print('\n🤖 Testing Agent Operations...\n')
    try:
        # Test 1: Agent Registration
        print('\n📋 Test: Agent Registration')
        agent_vc = await register_agent(RegisterAgentOptions(
            agent_name=AGENT_NAME,
            capabilities=CAPABILITIES,
            #developer_did=DEVELOPER_DID
        ), api_key=API_KEY)
        print('✅ Agent registration successful:', agent_vc)

        # Test 2: Authentication Token Generation
        print('\n🔐 Test: Authentication Token Generation')
        auth_token_data = await get_auth_token(GetAuthTokenOptions(
            agent_did=agent_vc['agentDid'],
            vc=agent_vc['vc'],
            audience='https://api.identitymachines.com',
            #developer_did=DEVELOPER_DID
        ), api_key=API_KEY)
        access_token = auth_token_data.get('access_token')
        if not access_token:
            print('❌ Failed to obtain access_token from authentication response.')
            return
        print('✅ Authentication token generated successfully:', access_token)

        # Test 3: Policy Upload
        print('\n🔐 Test: Policy Upload')
        policy_response = await upload_policy(UploadPolicyOptions(
            agent_did=agent_vc['agentDid'],
            config_type='opa',
            policy_content=POLICY_CONTENT,
            metadata={"version": "1.0", "description": "Read/write policy"},
            #developer_did=DEVELOPER_DID
        ), api_key=API_KEY)
        print('✅ Policy creation successful:', policy_response) # returns policy object (incl. policyId to use for decision)

        # Test 4: Policy Decision
        print('\n🔐 Test: Policy Decision')
        decision = await policy_decision(PolicyInput(
            agent_did=agent_vc['agentDid'],
            policy_id=policy_response['policyId'],
            token=access_token,
            action='write',
            resource='user-data',
            context={"user": "admin"}
        ), api_key=API_KEY)
        print('✅ Policy decision successful:', decision)

    except IronBookError as e:
        print('❌ Agent operations failed:', str(e))
    except Exception as e:
        print('❌ Unexpected error:', str(e))
    print('\n🎉 Agent operations test completed!')

async def run_all_tests():
    try:
        await test_agent_operations()
        print('\n✨ All tests completed successfully!')
    except Exception as e:
        print('\n💥 Test suite failed:', str(e))

if __name__ == '__main__':
    asyncio.run(run_all_tests())
