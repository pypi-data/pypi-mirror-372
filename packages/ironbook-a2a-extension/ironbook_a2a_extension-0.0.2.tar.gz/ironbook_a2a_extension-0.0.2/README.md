# Iron Book Extension (ironbook-a2a-extension)

## Overview

This extension defines how to enable Iron Book's zero trust policy-based access control for agents.

Server agents can choose to enforce Iron Book policies for incoming requests

## Extension URI

The URI of this extension is `https://github.com/identitymachines/ironbook-a2a-extension/v1`.

This is the only URI accepted for this extension.

## Messages Metadata Fields

Traceability information MUST be stored in the metadata for a Message or Artifact, under a
field with the key `github.com/a2aproject/a2a-samples/extensions/traceability/v1/traceability`,
or an addtional artifact in the returned completed response.


## Extension Activation

Clients indicate their desire to receive traceability on response by specifying
the [Extension URI](#extension-uri) via the transport-defined extension
activation mechanism. For JSON-RPC and HTTP transports, this is indicated via
the `X-A2A-Extensions` HTTP header. For gRPC, this is indicated via the
`X-A2A-Extensions` metadata value.
