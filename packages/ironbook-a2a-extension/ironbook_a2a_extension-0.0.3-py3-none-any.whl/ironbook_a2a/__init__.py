from a2a.types import AgentExtension

_CORE_PATH = 'github.com/identitymachines/ironbook-a2a-extension/v1'
IRONBOOK_EXTENSION_URI = f'https://{_CORE_PATH}'
IRONBOOK_AGENT_DID_FIELD = f'{_CORE_PATH}/agent-did'
IRONBOOK_AUTH_TOKEN_FIELD = f'{_CORE_PATH}/auth-token'
IRONBOOK_ACTION_FIELD = f'{_CORE_PATH}/action'
IRONBOOK_RESOURCE_FIELD = f'{_CORE_PATH}/resource'
IRONBOOK_CONTEXT_FIELD = f'{_CORE_PATH}/context'

class IronBookExtension:
    def agent_extension(self) -> AgentExtension:
        """Get the AgentExtension representing this extension."""
        return AgentExtension(
            uri=IRONBOOK_EXTENSION_URI,
            description='Enforces IronBook policies',
            required=True,
        )

__all__ = [
    'IronBookExtension',
    'IRONBOOK_EXTENSION_URI',
    'IRONBOOK_AGENT_DID_FIELD',
    'IRONBOOK_AUTH_TOKEN_FIELD',
    'IRONBOOK_ACTION_FIELD',
    'IRONBOOK_RESOURCE_FIELD',
    'IRONBOOK_CONTEXT_FIELD',
]
