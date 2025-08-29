# Python SDK

The `Python SDK` provides a simple way to verify agent identities using the Identity Platform's RESTful API. It is designed to be easy to use and integrate into Python applications.

## Prerequisites

To use the `Python SDK`, you need to have the following installed:

- [Python](https://www.python.org/downloads/) 3.8 or later

## Installation

To install the `Python SDK`, you can use `pip`:

```bash
pip install agntcy-identity-sdk
```

## Example Usage

To get and verify an agent's badge, you can use the following code snippet:

```python
import os

from agntcyidentity.sdk import IdentitySdk

# Initialize the Identity SDK
identity_sdk = IdentitySdk()

# Get badge by ID
badge = identity_sdk.get_badge("<ID>")
print("Got badge: ", badge)

# Verify badge
verified = identity_sdk.verify_badge(badge)
print("Badge verified: ", verified)

```

You must set the following environment variables:

- `IDENTITY_NODE_GRPC_SERVER_URL`: The URL of the Identity Node gRPC server.

> [!NOTE]
> If the node is running locally, you must add the following environment variable:
>
> - `IDENTITY_NODE_USE_SSL`: 0, to disable SSL verification.
