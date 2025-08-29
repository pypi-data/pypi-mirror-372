from aztp_client.common.types import (
    Identity,
    SecuredAgent,
    IssueIdentityRequest,
    Metadata,
)
from aztp_client.common.config import ClientConfig, whiteListTrustDomains
import socket
from datetime import datetime
from typing import Optional, Callable, Any, Dict, List, Union
import requests
from uuid import uuid4
import urllib3
import json
from dataclasses import dataclass
from pprint import pprint
import asyncio
import warnings
from .oidc.client import OIDCClient

# Global variable
globalName = None

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SecureConnection:
    """Secure wrapper for agents that provides identity verification while maintaining original functionality."""

    def __init__(self, agent: Any, identity: Identity, verify: Callable):
        """Initialize secure connection.

        Args:
            agent: The original agent being wrapped
            identity: AZTP identity information
            verify: Identity verification function
        """
        self._agent = agent
        self.identity = identity
        self.verify = verify

    def make_callable(self, func: Callable) -> Callable:
        """Create a secure callable that verifies identity before execution.

        Args:
            func: The original function to wrap

        Returns:
            Callable: A wrapped function that performs identity verification
        """
        async def wrapped(*args, **kwargs):
            # Verify identity before executing the function
            if not await self.verify():
                raise PermissionError("Identity verification failed")
            return await func(*args, **kwargs)
        return wrapped

    def __getattr__(self, name: str) -> Any:
        """Delegate any unknown attributes/methods to the wrapped agent.

        This enables transparent method delegation - any method call not handled
        by SecureConnection is passed through to the original agent with identity verification.

        Args:
            name: Name of the attribute/method being accessed

        Returns:
            The attribute/method from the wrapped agent, wrapped with identity verification if callable
        """
        attr = getattr(self._agent, name)
        if callable(attr) and asyncio.iscoroutinefunction(attr):
            return self.make_callable(attr)
        return attr


class Aztp:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        environment: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """Initialize AZTP client with optional configuration."""
        self.config = ClientConfig.create(
            api_key=api_key,
            base_url=base_url,
            environment=environment,
            timeout=timeout,
        )
        self.session = requests.Session()
        self.session.headers.update({
            "api_access_key": f"{self.config.api_key}",
            "Content-Type": "application/json",
        })
        print("API Key:", f"{self.config.api_key[:8]}...")
        
        # Initialize OIDC client
        self.oidc = OIDCClient(self.config)

    def _get_url(self, endpoint: str) -> str:
        """Get full URL for an endpoint."""
        # Just join the base URL with the endpoint
        base_url = self.config.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base_url}/{endpoint}"

    async def secure_connect(self, crew_agent: Optional[object] = None, name: Optional[str] = None, config: Optional[dict] = None) -> SecureConnection:
        """Create a secure connection for a workload.

        Args:
            crew_agent: Optional object representing the crew agent
            name: Name of the agent (required)
            config: Dictionary containing configuration options:
                - parentIdentity: Optional AZTP ID of the parent agent
                - trustDomain: Optional trust domain for the agent
                - isGlobalIdentity: Whether this is a global identity (default: False)

        Returns:
            SecureConnection: An object containing identity information and verify function
        """
        if not config or not isinstance(config, dict):
            raise ValueError("config parameter must be a dictionary")

        metadata = Metadata(
            hostname=socket.gethostname(),
            environment=self.config.environment,
        )

        globalName = name if config.get("isGlobalIdentity", False) else None

        request = IssueIdentityRequest(
            workload_id=name,
            agent_id="aztp",
            timestamp=datetime.now().astimezone().isoformat(),
            method="node",
            metadata=metadata,
        )

        # Convert request to dict and ensure proper casing for JSON
        request_data = {
            "workloadId": request.workload_id,
            "agentId": request.agent_id,
            "timestamp": request.timestamp,
            "isGlobalIdentity": config.get("isGlobalIdentity", False),
            "method": request.method,
            "metadata": {
                "hostname": request.metadata.hostname,
                "environment": request.metadata.environment,
                "extra": request.metadata.extra,
                "trustDomain": None,
                "parentIdentity": None
            }
        }

        # Add optional parameters if provided
        if config.get("trustDomain"):
            request_data["metadata"]["trustDomain"] = config["trustDomain"]
        if config.get("parentIdentity"):
            request_data["metadata"]["parentIdentity"] = config["parentIdentity"]

        url = self._get_url("aztp/issue-identity")

        try:
            response = self.session.post(
                url,
                json=request_data,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )

            response.raise_for_status()

            identity_data = response.json()

            # Get the data field from the response
            if isinstance(identity_data, dict) and 'data' in identity_data:
                identity_info = identity_data['data']

                if (identity_info.get("valid") is False):
                    aztp_id = identity_info.get("error")
                    valid = False
                else:
                    aztp_id = identity_info.get("aztpId")
                    valid = True

                workload_id = identity_info.get("workloadInfo").get("workloadId")

                # Create identity object
                identity = Identity(
                    aztp_id=aztp_id,
                    workload_id=workload_id,
                    valid=valid,
                    certificate="",
                    private_key="",
                    ca_certificate=""
                )

                # Create secured agent instance for verify function
                secured_agent = SecuredAgent(
                    name=name,
                    identity=identity,
                    metadata=metadata,
                )

                # Return SecureConnection instance with the original agent
                return SecureConnection(
                    agent=crew_agent,
                    identity=identity,
                    verify=lambda: self.verify_identity(secured_agent)
                )
            else:
                raise Exception(
                    "Invalid response format: missing 'data' field")
        except requests.exceptions.RequestException as e:
            print(f"\nRequest failed: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def verify_identity(self, agent: SecuredAgent, identity_flow_id: Optional[str] = None) -> bool:
        """Verify the identity of a secured agent.
        
        Args:
            agent: The SecuredAgent object containing identity information
            identity_flow_id: Optional identity flow ID for flow-specific verification
        """
        if not agent.identity:
            return False

        if (agent.identity.valid is False):
            return False

        # Prepare request data
        request_data = {"aztpId": agent.identity.aztp_id}
        
        # Add identity flow ID if provided
        if identity_flow_id:
            request_data["identityFlowId"] = identity_flow_id

        response = self.session.post(
            self._get_url("aztp/verify-identity"),
            json=request_data,
            timeout=self.config.timeout,
            verify=False,  # Disable SSL verification
        )
        response.raise_for_status()

        result = response.json()

        if isinstance(result, dict) and 'data' in result:
            if result.get("success") is True:
                return result['data'].get("valid", False)
            else:
                # Check if data exists and has a message before trying to access it
                if isinstance(result.get('data'), dict) and 'message' in result['data']:
                    print(result['data']['message'])
                elif 'message' in result:
                    print(result['message'])
                else:
                    print("Verification failed with no detailed message")
                return False
        else:
            return result.get("valid", False)

    async def verify_identity_by_aztp_id(
        self,
        aztp_id: str,
        identity_flow_id: Optional[str] = None
    ) -> bool:
        """Verify identity using only the AZTP ID.
        
        Args:
            aztp_id: The full AZTP ID to verify (required, must start with 'aztp://')
            identity_flow_id: Optional identity flow ID for flow-specific verification
            
        Returns:
            bool: True if identity is valid, False otherwise
            
        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If aztp_id is not provided or invalid
        """
        if not aztp_id:
            raise ValueError("aztp_id is required")
        if not aztp_id.startswith("aztp://"):
            raise ValueError("aztp_id must be a full AZTP ID starting with 'aztp://'")

        # Prepare request data
        request_data = {"aztpId": aztp_id}
        
        # Add identity flow ID if provided
        if identity_flow_id:
            request_data["identityFlowId"] = identity_flow_id

        try:
            response = self.session.post(
                self._get_url("aztp/verify-identity"),
                json=request_data,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()

            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                if result.get("success") is True:
                    return result['data'].get("valid", False)
                else:
                    # Check if data exists and has a message before trying to access it
                    if isinstance(result.get('data'), dict) and 'message' in result['data']:
                        print(result['data']['message'])
                    elif 'message' in result:
                        print(result['message'])
                    else:
                        print("Verification failed with no detailed message")
                    return False
            else:
                return result.get("valid", False)

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def verify_identity_using_agent_name(
        self,
        name: str,
        trust_domain: str = "aztp.network",
        workload: str = "workload",
        environment: str = "production",
        method: str = "node"
    ) -> bool:
        """Verify identity using agent name and optional parameters.

        This method allows verification of an agent's identity in two ways:
        1. Using a full AZTP ID (e.g., "aztp://aztp.network/workload/production/node/my-service")
        2. Using just the agent name with optional parameters to construct the AZTP ID

        Args:
            name: The agent name or full AZTP ID
                - If it starts with "aztp://", it will be used as-is
                - Otherwise, it will be combined with other parameters to form a full AZTP ID
            trust_domain: The trust domain (default: "aztp.network")
                This is typically your organization's domain
            workload: The workload identifier (default: "workload")
                This groups related services/agents
            environment: The deployment environment (default: "production")
                Common values: production, staging, development
            method: The authentication method (default: "node")
                Typically left as "node" unless using a different auth method

        Returns:
            bool: True if identity is valid, False otherwise
        """
        # If already a full AZTP ID, use as-is
        if name.startswith("aztp://"):
            print("Using existing AZTP ID:", name)
            aztp_id = name
        else:
            # Otherwise, construct the full AZTP ID with default values
            aztp_id = f"aztp://{trust_domain}/{workload}/{environment}/{method}/{name}"

        response = self.session.post(
            self._get_url("aztp/verify-identity"),
            json={"aztpId": aztp_id},
            timeout=self.config.timeout,
            verify=False,  # Disable SSL verification
        )
        response.raise_for_status()

        result = response.json()
        if isinstance(result, dict) and 'data' in result:
            return result['data'].get("valid", False)
        return result.get("valid", False)

    async def verify_authorize_identity_connection(self, fromAgentID: str, toAgentID: str, policyCode: str = None) -> bool:
        """Verify and authorize the connection between two secured agent's identity, with optional policyCode."""
        if not fromAgentID.startswith("aztp://") or not toAgentID.startswith("aztp://"):
            return False

        request_body = {
            "aztpId": fromAgentID,
            "requestAztpId": toAgentID
        }
        if policyCode:
            request_body["policyCode"] = policyCode

        response = self.session.post(
            self._get_url("aztp/authorize-connection-with-identities"),
            json=request_body,
            timeout=self.config.timeout,
            verify=False,  # Disable SSL verification
        )
        response.raise_for_status()

        result = response.json()
        if isinstance(result, dict) and 'data' in result:
            if result.get('success') is True and isinstance(result['data'], dict):
                return result['data'].get("valid", False)
            else:
                return False
        return result.get("valid", False)

    async def get_identity_by_name(self, name: str) -> dict:
        """Get identity information for a secured agent.

        Args:
            name: The name of the agent to get identity for

        Returns:
            dict: The identity information
        """

        try:
            response = self.session.get(
                self._get_url(f"aztp/get-identity/?agentName={name}"),
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                # Remove _id from the response data if it exists
                data = result['data']
                if 'selectors' in data:
                    del data['selectors']

                return json.dumps(data, indent=2)
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def get_identity(self, agent: SecureConnection) -> dict:
        """Get identity information for a secured agent.

        Args:
            agent: The SecureConnection object to get identity for

        Returns:
            dict: The identity information
        """
        if not agent.identity.workload_id:
            return None

        workload_id = agent.identity.workload_id

        try:
            response = self.session.get(
                self._get_url(f"aztp/get-identity/?agentName={workload_id}"),
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                # Remove _id from the response data if it exists
                data = result['data']
                if 'selectors' in data:
                    del data['selectors']

                return json.dumps(data, indent=2)
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def discover_identity(self, trust_domain: str = None, requestor_identity: str = None) -> dict:
        """Discover identities based on requestor identity and optional trust domain.

        This method allows agents to discover identities based on a requestor identity.
        It can optionally filter identities by a specified trust domain.

        Args:
            trust_domain: Optional trust domain to filter identities by (optional)
            requestor_identity: The AZTP ID of the requestor agent (optional)

        Returns:
            dict: List of discovered identities
        """

        if trust_domain and requestor_identity:
            response = self.session.get(
                self._get_url("aztp/discover-with-trust-domain"),
                params={
                    "trustDomain": trust_domain,
                    "aztpId": requestor_identity,
                },
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
        else:
            response = self.session.get(
                self._get_url("aztp/discoverable"),
                params={
                    "discoverable": True
                },
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
        response.raise_for_status()

        result = response.json()
        return json.dumps(result, indent=2)
        if isinstance(result, dict) and 'data' in result:
            return json.dumps(result, indent=2)
        else:
            raise Exception("Invalid response format: missing 'data' field")

    async def get_policy(self, aztp_id: str) -> dict:
        """Get access policy for a specific AZTP identity.

        Args:
            aztp_id: The full AZTP ID to get access policy for
                    (e.g. "aztp://domain/workload/environment/method/name")

        Returns:
            dict: The access policy information for the specified identity

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If the aztp_id is not properly formatted
        """
        if not aztp_id.startswith("aztp://"):
            raise ValueError(
                "aztp_id must be a full AZTP ID starting with 'aztp://'")

        try:
            response = self.session.get(
                self._get_url("aztp/get-identity-access-policy"),
                params={"aztpId": aztp_id},
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def revoke_identity(self, aztp_id: str, reason: str = None) -> dict:
        """Revoke an AZTP identity.

        Args:
            aztp_id: The full AZTP ID to revoke (e.g. "aztp://domain/workload/environment/method/name")
            reason: Optional reason for revoking the identity

        Returns:
            dict: The response data from the revocation request

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If the aztp_id is not properly formatted
        """
        if not aztp_id.startswith("aztp://"):
            raise ValueError(
                "aztp_id must be a full AZTP ID starting with 'aztp://'")

        request_data = {
            "aztpId": aztp_id,
        }
        if reason:
            request_data["reason"] = reason

        try:
            response = self.session.post(
                self._get_url("aztp/revoke-identity"),
                json=request_data,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return json.dumps(result['data'], indent=2)
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def reissue_identity(self, aztp_id: str) -> dict:
        """Reissue a previously revoked AZTP identity.

        Args:
            aztp_id: The full AZTP ID to unrevoke (e.g. "aztp://domain/workload/environment/method/name")

        Returns:
            dict: The response data from the unrevoke request

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If the aztp_id is not properly formatted
        """
        if not aztp_id.startswith("aztp://"):
            raise ValueError(
                "aztp_id must be a full AZTP ID starting with 'aztp://'")

        try:
            response = self.session.post(
                self._get_url("aztp/reissue-revoked-identity"),
                json={"aztpId": aztp_id},
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return json.dumps(result['data'], indent=2)
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    def get_policy_value(self, policies: list, filter_key: str, filter_value: str) -> Optional[dict]:
        """
        Filters the access policy data by a key-value pair and returns the policyStatement if found.

        Args:
            policies: List of policy dicts (typically from get_policy)
            filter_key: The key to match (e.g., 'code', 'policyName')
            filter_value: The exact value to match

        Returns:
            The matched policyStatement dict or None
        """
        for policy in policies:
            if policy.get(filter_key) == filter_value:
                return policy.get("policyStatement")
        return None

    def is_action_allowed(self, policy: dict, action: str) -> bool:
        """
        Is action allowed by policy
        Args:
            policy: The policyStatement dict to check
            action: The action to check
        Returns:
            True if the action is allowed, False otherwise
        """
        if not policy or 'Statement' not in policy:
            return False

        statements = policy['Statement']
        # Statement can be a dict or a list
        if isinstance(statements, dict):
            statements = [statements]

        for stmt in statements:
            actions = stmt.get('Action')
            if actions is None:
                continue
            # Action can be a string or a list
            if not isinstance(actions, list):
                actions = [actions]
            effect = stmt.get('Effect')
            if action in actions and effect in ("Allow", "Audit"):
                return True
        return False

    async def link_identities(
        self,
        source_identity: str,
        target_identity: str,
        relationship_type: str = "linked",
        metadata: Optional[Dict] = None
    ) -> dict:
        """Link two workload identities together.

        This method creates a relationship link between two workload identities.
        The relationship can be either 'linked' (peer relationship) or 'parent' (hierarchical).

        Args:
            source_identity: The full AZTP ID of the source identity
                            (e.g. "aztp://domain/workload/environment/method/name")
            target_identity: The full AZTP ID of the target identity to link to
                            (e.g. "aztp://domain/workload/environment/method/name")
            relationship_type: Type of relationship between identities, either "linked" or "parent"
                              (default: "linked")
            metadata: Optional dictionary containing additional metadata for the link
                     Such as security context information

        Returns:
            dict: The response data containing information about the created link

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If the identity IDs are not properly formatted or relationship_type is invalid
        """
        # Validate AZTP IDs
        if not source_identity.startswith("aztp://"):
            raise ValueError(
                "source_identity must be a full AZTP ID starting with 'aztp://'")
        if not target_identity.startswith("aztp://"):
            raise ValueError(
                "target_identity must be a full AZTP ID starting with 'aztp://'")

        # Validate relationship type
        if relationship_type not in ["linked", "parent"]:
            raise ValueError(
                "relationship_type must be either 'linked' or 'parent'")

        # Prepare request data
        request_data = {
            "sourceIdentity": source_identity,
            "targetIdentity": target_identity,
            "relationshipType": relationship_type
        }

        # Add metadata if provided
        if metadata:
            request_data["metadata"] = metadata

        try:
            response = self.session.post(
                self._get_url("aztp/create-workload-identity-link"),
                json=request_data,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def check_identity_policy_permissions(
        self,
        aztp_id: str,
        options: Optional[dict] = None
    ) -> dict:
        """
        Gets action permissions for an identity based on policy and action(s).
        Args:
            aztp_id: The AZTP ID (required, must start with 'aztp://')
            options: Optional dict with keys 'policy_code' (or 'policyCode'), 'actions', 'trust_domain' (or 'trustDomain')
        Returns:
            dict: The API response containing action permissions
        Raises:
            ValueError: If aztp_id is missing or invalid
            requests.exceptions.RequestException: If the request fails
        """
        if not aztp_id or not aztp_id.startswith("aztp://"):
            raise ValueError(
                "aztp_id must be a full AZTP ID starting with 'aztp://'!")

        policy_code = None
        actions = None
        trust_domain = None
        if options and isinstance(options, dict):
            policy_code = options.get(
                "policy_code") or options.get("policyCode")
            actions = options.get("actions")
            trust_domain = options.get(
                "trust_domain") or options.get("trustDomain")

        params = {"aztpId": aztp_id}
        if policy_code:
            if policy_code.startswith("policy:"):
                params["policy_code"] = policy_code
            else:
                params["policy_id"] = policy_code
        if actions:
            if isinstance(actions, list):
                params["action"] = ",".join(actions)
            else:
                params["action"] = actions
        if trust_domain:
            params["trust_domain"] = trust_domain

        try:
            response = self.session.get(
                self._get_url("aztp/get-identity-action-permissions"),
                params=params,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()
            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    # Identity Flows Methods

    async def flow_health(self) -> dict:
        """Get the health of the identity flow service.

        Returns:
            dict: The response data containing information about the health of the identity flow service
        """
        try:
            response = self.session.get(
                self._get_url("identity-flow/health"),
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise
        
    
    async def create_flow(
        self,
        name: str,
        description: Optional[str] = None,
        discoverable: str = "public",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> dict:
        """Create a new identity flow.

        Args:
            name: The name for the new identity flow (required)
            description: Optional description for the flow
            discoverable: Discoverability setting for the flow (default: "public" accepts "public", "private")
            tags: Optional list of tags for the flow
            metadata: Optional dictionary containing additional metadata for the flow
                     Can include astha-flow reference with id and folderId

        Returns:
            dict: The response data containing information about the created flow

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If name is not provided
        """
        if not name:
            raise ValueError("name is required")

        # Prepare request data
        request_data = {
            "name": name,
            "discoverable": discoverable
        }

        # Add optional parameters if provided
        if description is not None:
            request_data["description"] = description
        if tags is not None:
            request_data["tags"] = tags
        if metadata is not None:
            request_data["metadata"] = metadata

        try:
            response = self.session.post(
                self._get_url("identity-flow/create"),
                json=request_data,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def update_flow(
        self,
        flow_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        discoverable: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> dict:
        """Update an existing identity flow.

        Args:
            flow_id: The ID of the flow to update (required)
            name: Optional new name for the flow
            description: Optional new description for the flow
            discoverable: Optional discoverability setting for the flow (accepts "public", "private")
            tags: Optional list of tags for the flow

        Returns:
            dict: The response data containing information about the updated flow

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If flow_id is not provided
        """
        if not flow_id:
            raise ValueError("flow_id is required")

        # Prepare request data - only include non-None values
        request_data = {}

        # Add optional parameters if provided
        if name is not None:
            request_data["name"] = name
        if description is not None:
            request_data["description"] = description
        if discoverable is not None:
            request_data["discoverable"] = discoverable
        if tags is not None:
            request_data["tags"] = tags

        try:
            response = self.session.put(
                self._get_url(f"identity-flow/update/{flow_id}"),
                json=request_data,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def delete_flow(self, flow_id: str) -> dict:
        """Delete an identity flow.

        Args:
            flow_id: The ID of the flow to delete (required)

        Returns:
            dict: The response data confirming the deletion

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If flow_id is not provided
        """
        if not flow_id:
            raise ValueError("flow_id is required")

        try:
            response = self.session.delete(
                self._get_url(f"identity-flow/delete/{flow_id}"),
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def add_identity_to_flow(
        self,
        identity_flow_id: str,
        aztp_id: str
    ) -> dict:
        """Add an identity to an existing flow.

        Args:
            identity_flow_id: The ID of the identity flow to add the identity to (required)
            aztp_id: The full AZTP ID to add to the flow (required, must start with 'aztp://')

        Returns:
            dict: The response data confirming the addition

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If identity_flow_id or aztp_id are not provided or aztp_id is invalid
        """
        if not identity_flow_id:
            raise ValueError("identity_flow_id is required")
        if not aztp_id:
            raise ValueError("aztp_id is required")
        if not aztp_id.startswith("aztp://"):
            raise ValueError("aztp_id must be a full AZTP ID starting with 'aztp://'")

        # Prepare request data
        request_data = {
            "identityFlowId": identity_flow_id,
            "identity": {
                "aztpId": aztp_id
            }
        }

        try:
            response = self.session.post(
                self._get_url("identity-flow/add-identity-to-flow"),
                json=request_data,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def remove_identity_from_flow(
        self,
        identity_flow_id: str,
        aztp_id: str
    ) -> dict:
        """Remove an identity from a flow.

        Args:
            identity_flow_id: The ID of the identity flow to remove the identity from (required)
            aztp_id: The full AZTP ID to remove from the flow (required, must start with 'aztp://')

        Returns:
            dict: The response data confirming the removal

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If identity_flow_id or aztp_id are not provided or aztp_id is invalid
        """
        if not identity_flow_id:
            raise ValueError("identity_flow_id is required")
        if not aztp_id:
            raise ValueError("aztp_id is required")
        if not aztp_id.startswith("aztp://"):
            raise ValueError("aztp_id must be a full AZTP ID starting with 'aztp://'")

        # Prepare request data
        request_data = {
            "identityFlowId": identity_flow_id,
            "aztpId": aztp_id
        }

        try:
            response = self.session.post(
                self._get_url("identity-flow/remove-identity-from-flow"),
                json=request_data,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    async def revoke_flow_identity(
        self,
        aztp_id: str,
        identity_flow_id: str,
        reason: str
    ) -> dict:
        """Revoke an identity from a flow.

        Args:
            aztp_id: The full AZTP ID to revoke from the flow (required, must start with 'aztp://')
            identity_flow_id: The ID of the identity flow (required)
            reason: Reason for revoking the identity (required)

        Returns:
            dict: The response data confirming the revocation

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If aztp_id, identity_flow_id, or reason are not provided or aztp_id is invalid
        """
        if not aztp_id:
            raise ValueError("aztp_id is required")
        if not aztp_id.startswith("aztp://"):
            raise ValueError("aztp_id must be a full AZTP ID starting with 'aztp://'")
        if not identity_flow_id:
            raise ValueError("identity_flow_id is required")
        if not reason:
            raise ValueError("reason is required")

        # Prepare request data
        request_data = {
            "aztpId": aztp_id,
            "identityFlowId": identity_flow_id,
            "reason": reason
        }

        try:
            response = self.session.post(
                self._get_url("aztp/revoke-identity-for-flow"),
                json=request_data,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise
    
    # Organization Identity Access Policy (OIAP)

    async def oiap_evaluate(
        self,
        aztp_id: str,
        requested_resource: str,
        user_id: str
    ) -> dict:
        """Evaluate Organization Identity Access Policy (OIAP) for a given identity, resource, and user.

        Args:
            aztp_id: The full AZTP ID to evaluate (required, must start with 'aztp://')
            requested_resource: The resource being requested access to (required)
            user_id: The user ID making the request (required)

        Returns:
            dict: The response data containing the OIAP evaluation result

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If any required parameter is missing or aztp_id is invalid
        """
        if not aztp_id:
            raise ValueError("aztp_id is required")
        if not aztp_id.startswith("aztp://"):
            raise ValueError("aztp_id must be a full AZTP ID starting with 'aztp://'")
        if not requested_resource:
            raise ValueError("requested_resource is required")
        if not user_id:
            raise ValueError("user_id is required")

        # Prepare request data
        request_data = {
            "aztp_id": aztp_id,
            "requested_resource": requested_resource,
            "user_id": user_id
        }

        try:
            response = self.session.post(
                self._get_url("oiap/evaluate"),
                json=request_data,
                timeout=self.config.timeout,
                verify=False,  # Disable SSL verification
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise
    
    