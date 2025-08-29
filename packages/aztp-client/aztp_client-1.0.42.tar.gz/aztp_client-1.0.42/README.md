# AZTP Client Python

Enterprise-grade identity service client for secure workload identity management using AZTP standards.

---

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Trusted Domains](#trusted-domains)
- [Quick Start](#quick-start)
- [Core Methods](#core-methods)
  - [Identity Management](#identity-management)
  - [Policy Management](#policy-management)
  - [Identity Flows Management](#identity-flows-management)
  - [OIAP Evaluation](#oiap-evaluation)
  - [OIDC Authentication](#oidc-authentication)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [License](#license)

---

## Installation

```bash
pip install aztp-client
```

## Requirements

- Python 3.8 or higher
- aiohttp (for OIDC functionality)

---

## Trusted Domains

The AZTP client maintains a whitelist of trusted domains for use with the `trustDomain` parameter. If not specified, defaults to `aztp.network`.

```python
from aztp_client import whiteListTrustDomains
print("Available trusted domains:", whiteListTrustDomains)
```

**Current Trusted Domains:**

- `gptarticles.xyz`
- `gptapps.ai`
- `vcagents.ai`

---

## Quick Start

```python
from aztp_client import Aztp

client = Aztp(api_key="your-api-key")
agent = await client.secure_connect({}, "service1", config={"isGlobalIdentity": False})
```

---

## Core Methods

### Identity Management

| Method                                                                            | Description                                                                         |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `secure_connect(crew_agent, name, config)`                                        | Create a secure connection for a workload                                           |
| `verify_identity(agent, identity_flow_id=None)`                                   | Verify the identity of a secured agent (optionally within a specific flow)          |
| `verify_identity_by_aztp_id(aztp_id, identity_flow_id=None)`                      | Verify identity using only the AZTP ID (optionally within a specific flow)          |
| `verify_authorize_identity_connection(from_aztp_id, to_aztp_id, policyCode=None)` | Verify and authorize connection between two agents (optionally using a policy code) |
| `get_identity(agent)`                                                             | Get identity information for a secured agent                                        |
| `get_identity_by_name(name)`                                                      | Get identity information by name                                                    |
| `discover_identity(trust_domain, requestor_identity)`                             | Discover identities based on parameters                                             |
| `revoke_identity(aztp_id, reason)`                                                | Revoke an AZTP identity                                                             |
| `reissue_identity(aztp_id)`                                                       | Restore a previously revoked identity                                               |
| `link_identities(source_identity, target_identity, relationship_type, metadata)`  | Link two workload identities together                                               |

### Policy Management

| Method                                                 | Description                                                                       |
| ------------------------------------------------------ | --------------------------------------------------------------------------------- |
| `get_policy(aztp_id)`                                  | Get access policy for a specific AZTP identity                                    |
| `get_policy_value(policies, filter_key, filter_value)` | Filter and extract a specific policy statement                                    |
| `is_action_allowed(policy, action)`                    | Check if an action is allowed by a policy statement                               |
| `check_identity_policy_permissions(aztp_id, options)`  | Get action permissions for an identity based on policy, actions, and trust domain |
| `oiap_evaluate(aztp_id, requested_resource, user_id)`  | Evaluate Organization Identity Access Policy for a specific resource and user     |

### Identity Flows Management

Identity Flows provide a way to group and manage multiple identities together in organized workflows. This feature enables you to create, manage, and control collections of identities for complex scenarios like multi-service deployments, testing environments, or development workflows.

| Method                                                         | Description                                             |
| -------------------------------------------------------------- | ------------------------------------------------------- |
| `create_flow(name, description, discoverable, tags, metadata)` | Create a new identity flow with specified configuration |
| `update_flow(flow_id, name, description, discoverable, tags)`  | Update an existing identity flow                        |
| `delete_flow(flow_id)`                                         | Delete an identity flow                                 |
| `add_identity_to_flow(identity_flow_id, aztp_id)`              | Add an existing identity to a flow                      |
| `remove_identity_from_flow(identity_flow_id, aztp_id)`         | Remove an identity from a flow                          |
| `revoke_flow_identity(aztp_id, identity_flow_id, reason)`      | Revoke an identity specifically from a flow context     |

#### Flow Configuration Options

When creating flows, you can customize them with the following options:

- **discoverable**: Controls flow visibility

  - `"public"` - Flow is discoverable by others (default)
  - `"private"` - Flow is only accessible to the creator

- **metadata**: Additional flow information
  - Can include integration references (e.g., `astha-flow` with `id` and `folderId`)
  - Custom project or environment metadata
  - Any JSON-serializable data

#### Quick Start: Identity Flows

```python
# 1. Create a flow
flow = await client.create_flow("my-flow", description="My workflow")

# 2. Add identities to the flow
await client.add_identity_to_flow(flow["_id"], "aztp://domain/workload/prod/node/service1")

# 3. Verify identity within flow context
is_valid = await client.verify_identity_by_aztp_id(
    "aztp://domain/workload/prod/node/service1",
    identity_flow_id=flow["_id"]
)

# 4. Manage flow lifecycle
await client.update_flow(flow["_id"], name="updated-flow")
await client.delete_flow(flow["_id"])  # When done
```

### OIAP Evaluation

OIAP (Organization Identity Access Policy) Evaluation allows you to determine whether a specific user has access to a requested resource based on the identity's access policies. This is essential for implementing fine-grained access control in your applications.

| Method                                                | Description                                                                   |
| ----------------------------------------------------- | ----------------------------------------------------------------------------- |
| `oiap_evaluate(aztp_id, requested_resource, user_id)` | Evaluate Organization Identity Access Policy for a specific resource and user |

#### Method Details

```python
async def oiap_evaluate(
    aztp_id: str,
    requested_resource: str,
    user_id: str
) -> dict:
```

**Parameters:**

- **aztp_id** (str): The full AZTP ID to evaluate (must start with 'aztp://')
  - Example: `"aztp://aztp.network.local/workload/production/node/somit/samba"`
- **requested_resource** (str): The resource being requested access to
  - Examples: `"user_list"`, `"database_read"`, `"file_write"`
- **user_id** (str): The user ID making the request
  - Example: `"674586f9cb96f7fe5538f334"`

**Returns:**

- **dict**: The response data containing the OIAP evaluation result

#### Quick Start: OIAP Evaluation

```python
# Basic OIAP evaluation
result = await client.oiap_evaluate(
    aztp_id="aztp://aztp.network.local/workload/production/node/service1",
    requested_resource="user_list",
    user_id="674586f9cb96f7fe5538f334"
)
print(f"Access granted: {result}")
```

#### Policy Statement Structure

- The `Statement` field in a policy can be either a single dict or a list of dicts.
- The `Action` field can be a string or a list of strings.
- The `is_action_allowed` method normalizes both cases and works for all valid policy structures.

#### Example: Check if an action is allowed

```python
policy_statement = aztpClient.get_policy_value(identity_access_policy, "code", "policy:0650537f8614")
if policy_statement:
    is_allowed = aztpClient.is_action_allowed(policy_statement, "read")
    print(f"Is 'read' allowed? {is_allowed}")
```

**Example Policy Statement:**

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["read", "write"]
    },
    {
      "Effect": "Deny",
      "Action": "delete"
    }
  ]
}
```

### Example: Verify and Authorize Identity Connection

```python
# Verify and authorize the connection between two agents (optionally with a policy code)
from_aztp_id = "aztp://example.com/workload/production/node/agentA"
to_aztp_id = "aztp://example.com/workload/production/node/agentB"

# Basic usage (no policy code)
is_valid_connection = await aztpClient.verify_authorize_identity_connection(from_aztp_id, to_aztp_id)
print("Connection valid:", is_valid_connection)

# With a policy code
default_policy_code = "policy:1234567890abcdef"
is_valid_connection = await aztpClient.verify_authorize_identity_connection(from_aztp_id, to_aztp_id, policyCode=default_policy_code)
print("Connection valid with policy:", is_valid_connection)
```

### Example: Enhanced Identity Verification

The AZTP client now supports enhanced identity verification methods that can work within identity flow contexts:

```python
import asyncio
from aztp_client import Aztp

async def enhanced_verification_examples():
    client = Aztp(api_key="your-api-key")

    # Create a secured agent
    agent = await client.secure_connect({}, "my-service", {"isGlobalIdentity": False})

    # Method 1: Traditional verification (works as before)
    is_valid = await client.verify_identity(agent)
    print(f"Traditional verification: {is_valid}")

    # Method 2: Verification with identity flow context
    flow_id = "your-flow-id"  # From create_flow response
    is_valid_in_flow = await client.verify_identity(agent, identity_flow_id=flow_id)
    print(f"Verification in flow context: {is_valid_in_flow}")

    # Method 3: Direct verification using AZTP ID
    aztp_id = "aztp://example.com/workload/production/node/my-service"
    is_valid_direct = await client.verify_identity_by_aztp_id(aztp_id)
    print(f"Direct AZTP ID verification: {is_valid_direct}")

    # Method 4: Direct verification with flow context
    is_valid_direct_flow = await client.verify_identity_by_aztp_id(aztp_id, identity_flow_id=flow_id)
    print(f"Direct verification in flow: {is_valid_direct_flow}")

# Run the example
asyncio.run(enhanced_verification_examples())
```

### OIDC Authentication

The AZTP client includes support for OpenID Connect (OIDC) authentication, allowing you to integrate with various identity providers.

#### OIDC Methods

| Method                                   | Description                                   |
| ---------------------------------------- | --------------------------------------------- |
| `oidc.login(provider, aztp_id, options)` | Initiate OIDC login with a specified provider |
| `oidc.validate_token(token)`             | Validate a JWT token and get user information |

#### OIDC Login Options

The `login` method accepts the following options:

```python
options = {
    "return_url": str,     # Optional callback URL
    "stateless": bool      # Whether to use stateless authentication (default: True)
}
```

#### Example: OIDC Authentication

```python
import asyncio
from aztp_client import Aztp

async def main():
    # Initialize the AZTP client
    client = Aztp(
        api_key="your_api_key"
    )

    # Example 1: Initiate OIDC login with Google
    try:
        login_response = await client.oidc.login(
            provider="google",
            aztp_id="aztp://example.com/workload/production/node/my-service",
            options={
                "return_url": "https://your-app.com/callback"
            }
        )
        print("Redirect URL:", login_response["redirectUrl"])
    except Exception as e:
        print("Login failed:", str(e))

    # Example 2: Validate a token
    try:
        token = "your_token_here"  # Replace with actual token
        validation_response = await client.oidc.validate_token(token)

        if validation_response["valid"]:
            print("User Info:")
            print(f"  Name: {validation_response['user']['name']}")
            print(f"  Email: {validation_response['user']['email']}")
            print(f"  Provider: {validation_response['user']['provider']}")
    except Exception as e:
        print("Token validation failed:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
```

#### OIDC Response Types

**Login Response:**

```python
{
    "success": bool,
    "message": str,
    "redirect_url": str,
    "state": str,
    "token": Optional[str]
}
```

**Token Validation Response:**

```python
{
    "success": bool,
    "valid": bool,
    "user": {
        "sub": str,
        "email": str,
        "name": str,
        "provider": str,
        "agent": str
    },
    "token_type": str,
    "message": str
}
```

---

## Examples

### Complete Identity Flows Workflow

```python
import os
import asyncio
from aztp_client import Aztp
from dotenv import load_dotenv

load_dotenv()

async def identity_flows_example():
    """Complete example demonstrating Identity Flows functionality."""

    # Initialize the AZTP client
    client = Aztp(
        api_key=os.getenv("AZTP_API_KEY"),
        base_url=os.getenv("AZTP_BASE_URL")
    )

    try:
        # Step 1: Create a new identity flow
        print("\nCreating new identity flow...")
        flow = await client.create_flow(
            name="microservices-deployment",
            description="Flow for managing microservices deployment identities",
            discoverable="public",  # "public" or "private"
            tags=["microservices", "deployment", "production"],
            metadata={
                "project": "my-project",
                "environment": "production",
                "astha-flow": {
                    "id": "flow-12345",
                    "folderId": "folder-67890"
                }
            }
        )
        print(f"Flow created: {flow['_id']}")
        flow_id = flow["_id"]

        # Step 2: Create some identities and add them to the flow
        print("\nCreating identities and adding to flow...")

        # Create identities for different services
        service_names = ["user-service", "payment-service", "notification-service"]
        service_agents = []

        for service_name in service_names:
            # Create secure agent
            agent = await client.secure_connect(
                {},
                service_name,
                {"isGlobalIdentity": False}
            )
            service_agents.append(agent)

            # Add identity to flow
            result = await client.add_identity_to_flow(
                identity_flow_id=flow_id,
                aztp_id=agent.identity.aztp_id
            )
            print(f"Added {service_name} to flow: {result}")

        # Step 3: Verify identities within flow context
        print("\nVerifying identities within flow context...")
        for agent in service_agents:
            is_valid = await client.verify_identity(agent, identity_flow_id=flow_id)
            print(f"Identity {agent.identity.aztp_id} valid in flow: {is_valid}")

            # Also demonstrate direct verification by AZTP ID
            is_valid_direct = await client.verify_identity_by_aztp_id(
                agent.identity.aztp_id,
                identity_flow_id=flow_id
            )
            print(f"Direct verification result: {is_valid_direct}")

        # Step 4: Update the flow
        print("\nUpdating flow...")
        updated_flow = await client.update_flow(
            flow_id=flow_id,
            name="microservices-deployment-updated",
            description="Updated flow description",
            tags=["microservices", "deployment", "production", "updated"]
        )
        print(f"Flow updated: {updated_flow}")

        # Step 5: Demonstrate flow-specific identity revocation
        print("\nRevoking one identity from flow...")
        if service_agents:
            revoke_result = await client.revoke_flow_identity(
                aztp_id=service_agents[0].identity.aztp_id,
                identity_flow_id=flow_id,
                reason="Service being decommissioned"
            )
            print(f"Identity revoked from flow: {revoke_result}")

        # Step 6: Remove an identity from flow (different from revocation)
        print("\nRemoving identity from flow...")
        if len(service_agents) > 1:
            remove_result = await client.remove_identity_from_flow(
                identity_flow_id=flow_id,
                aztp_id=service_agents[1].identity.aztp_id
            )
            print(f"Identity removed from flow: {remove_result}")

        # Step 7: Verify remaining identities
        print("\nVerifying remaining identities...")
        for i, agent in enumerate(service_agents):
            try:
                is_valid = await client.verify_identity_by_aztp_id(
                    agent.identity.aztp_id,
                    identity_flow_id=flow_id
                )
                print(f"Service {i}: {is_valid}")
            except Exception as e:
                print(f"Service {i}: Verification failed - {e}")

        # Optional: Clean up - delete the flow
        # print(f"\nDeleting flow {flow_id}...")
        # delete_result = await client.delete_flow(flow_id)
        # print(f"Flow deleted: {delete_result}")

    except Exception as e:
        print(f"Error in identity flows example: {e}")

if __name__ == "__main__":
    asyncio.run(identity_flows_example())
```

### Identity Revocation and Reissue

````python
import os
import asyncio
from aztp_client import Aztp, whiteListTrustDomains
from dotenv import load_dotenv

load_dotenv()

async def main():
    api_key = os.getenv("AZTP_API_KEY")
    base_url = os.getenv("AZTP_BASE_URL")
    if not api_key:
        raise ValueError("AZTP_API_KEY is not set")

    aztpClient = Aztp(api_key=api_key, base_url=base_url)
    agent = {}
    agent_name = "astha-local/arjun"

    # Secure Connect
    print(f"Connecting agent: {agent_name}")
    localTestAgent = await aztpClient.secure_connect(agent, agent_name, {"isGlobalIdentity": False})
    print("AZTP ID:", localTestAgent.identity.aztp_id)

    # Verify
    print(f"Verifying identity for agent: {agent_name}")
    verify = await aztpClient.verify_identity(localTestAgent)
    print("Verify:", verify)

    # Revoke identity
    print(f"Revoking identity for agent: {agent_name}")
    revoke_result = await aztpClient.revoke_identity(localTestAgent.identity.aztp_id, "Revoked by user")
    print("Identity Revoked:", revoke_result)

    # Verify after revoke
    print(f"Verifying identity after revoke for agent: {agent_name}")
    is_valid_after_revoke = await aztpClient.verify_identity(localTestAgent)
    print("Identity Valid After Revoke:", is_valid_after_revoke)

    # Reissue identity
    print(f"Reissuing identity for agent: {agent_name}")
    reissue_result = await aztpClient.reissue_identity(localTestAgent.identity.aztp_id)
    print("Identity Reissued:", reissue_result)

    # Verify after reissue
    print(f"Verifying identity after reissue for agent: {agent_name}")
    is_valid_after_reissue = await aztpClient.verify_identity(localTestAgent)
    print("Identity Valid After Reissue:", is_valid_after_reissue)

    # Get and display policy information
    print(f"Getting policy information for agent: {agent_name}")
    identity_access_policy = await aztpClient.get_policy(localTestAgent.identity.aztp_id)

    # Extract a specific policy by code (replace with your actual policy code)
    policy = aztpClient.get_policy_value(
        identity_access_policy,
        "code",
        "policy:0650537f8614"  # Replace with your actual policy code
    )

    if policy:
        is_allow = aztpClient.is_action_allowed(policy, "read")
        print({"is_allow": is_allow})
        if is_allow:
            print({"actions": actions})
    else:
        print("Policy not found.")

        # Link identities
    print(f"Linking {agent_name}'s identity to another service")
    try:
        target_identity = "aztp://astha.ai/workload/production/node/partner-service"
        link_result = await aztpClient.link_identities(
            localTestAgent.identity.aztp_id,
            target_identity,
            "linked"
        )
        print(f"Identities linked successfully. Link ID: {link_result.get('_id')}")
    except Exception as e:
        print(f"Failed to link identities: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

### Linking Identities

```python
import os
import asyncio
from aztp_client import Aztp
from dotenv import load_dotenv

load_dotenv()

async def main():
    api_key = os.getenv("AZTP_API_KEY")
    base_url = os.getenv("AZTP_BASE_URL")
    if not api_key:
        raise ValueError("AZTP_API_KEY is not set")

    aztpClient = Aztp(api_key=api_key, base_url=base_url)

    # Define the source and target identities
    source_identity = "aztp://astha.ai/workload/production/node/service-a"
    target_identity = "aztp://astha.ai/workload/production/node/service-b"

    # Link the two identities with a peer relationship
    try:
        result = await aztpClient.link_identities(
            source_identity=source_identity,
            target_identity=target_identity,
            relationship_type="linked",  # Can be "linked" or "parent"
        )
        print("Identity link created successfully:")
        print(f"Link ID: {result.get('_id')}")
        print(f"Source: {result.get('sourceIdentity')}")
        print(f"Target: {result.get('targetIdentity')}")
        print(f"Relationship: {result.get('relationshipType')}")
    except Exception as e:
        print(f"Error linking identities: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

### OIAP Evaluation Example

```python
import asyncio
import os
from aztp_client import Aztp
from dotenv import load_dotenv

load_dotenv()

async def oiap_evaluation_example():
    """Complete example demonstrating OIAP evaluation functionality"""

    # Initialize AZTP client
    client = Aztp(
        api_key=os.getenv("AZTP_API_KEY"),
        base_url=os.getenv("AZTP_BASE_URL")
    )

    try:
        # Basic OIAP evaluation
        result = await client.oiap_evaluate(
            aztp_id="aztp://astha.ai/workload/production/node/service-a",
            requested_resource="user_list",
            user_id="674586f9cb96f7fe5538f334"
        )

        print("✅ OIAP Evaluation successful!")
        print(f"Access result: {result}")

    except ValueError as ve:
        print(f"❌ Validation Error: {ve}")
    except Exception as e:
        print(f"❌ Request Error: {e}")

if __name__ == "__main__":
    asyncio.run(oiap_evaluation_example())
```

### Check Identity Policy Permissions

```python
# aztp_id is the full AZTP identity string
aztp_id = "aztp://aztp.local/workload/production/node/aj-agent-172"

# 1. Get all action permissions for an identity
permissions = await aztpClient.check_identity_policy_permissions(aztp_id)
print("Permissions (default):", permissions)

# 2. Get permissions for a specific policy
permissions_policy = await aztpClient.check_identity_policy_permissions(
    aztp_id,
    options={"policy_code": "policy:1589246d7b16"}
)
print("Permissions (policy_code):", permissions_policy)

# 3. Get permissions for specific actions
permissions_actions = await aztpClient.check_identity_policy_permissions(
    aztp_id,
    options={"actions": ["list_users", "read"]}
)
print("Permissions (actions):", permissions_actions)

# 4. Get permissions for a specific trust domain
permissions_trust = await aztpClient.check_identity_policy_permissions(
    aztp_id,
    options={"trust_domain": "aztp.network"}
)
print("Permissions (trust_domain):", permissions_trust)

# 5. Get permissions with all options
permissions_all = await aztpClient.check_identity_policy_permissions(
    aztp_id,
    options={
        "policy_code": "policy:1589246d7b16",
        "actions": ["read", "write"],
        "trust_domain": "aztp.network"
    }
)
print("Permissions (all options):", permissions_all)

# Note: You can use either snake_case or camelCase keys in the options dict.
````

---

## Error Handling

- **Connection Errors**: Handles network and server connectivity issues
- **Authentication Errors**: Manages API key and authentication failures
- **Validation Errors**: Validates input parameters and trust domains
- **Policy Errors**: Handles policy retrieval and validation failures

---

## License

MIT License
