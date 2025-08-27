# Iron Book Extension (ironbook-a2a-extension)

## Overview

This extension defines how to enable Iron Book's zero trust policy-based access control for agents.

## Extension URI

The URI of this extension is `https://github.com/identitymachines/ironbook-a2a-extension/v1`.

This is the only URI accepted for this extension.

## Messages Metadata Fields

Messages from the client agent MUST include the following metadata fields:
- Agent DID: `https://github.com/identitymachines/ironbook-a2a-extension/v1/agent-did`
- Auth token: `https://github.com/identitymachines/ironbook-a2a-extension/v1/auth-token`
- Action: `https://github.com/identitymachines/ironbook-a2a-extension/v1/action`
- Resource: `https://github.com/identitymachines/ironbook-a2a-extension/v1/resource`
- Context: `https://github.com/identitymachines/ironbook-a2a-extension/v1/context`

## Process

If a client agent wishes to send a message to a server agent that enforces Iron Book policies, the client agent MUST:

1. [Activate](#extension-activation) the IronBook A2A extension.
1. Use the Iron Book SDK or portal to register the agent.
1. Use the Iron Book SDK to get an auth token.
1. Include the [Message metadata fields](#messages-metadata-fields).

The server agent MUST:

1. Validate that the Message metadata fields are provided.
    1. If fields are missing, it MUST return an error.
1. Use the Iron Book SDK to submit a policy decision request.
    1. If allowed, the Message will be processed.
    1. If denied, it MUST return an error.

## Extension Activation

Clients indicate their desire to receive traceability on response by specifying
the [Extension URI](#extension-uri) via the transport-defined extension
activation mechanism. For JSON-RPC and HTTP transports, this is indicated via
the `X-A2A-Extensions` HTTP header. For gRPC, this is indicated via the
`X-A2A-Extensions` metadata value.
