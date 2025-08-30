"""
Calimero Network Python Client SDK v2 - Rust-based Implementation

This module provides a unified Calimero client that wraps the Rust implementation
via Python bindings, offering better performance and more features.
"""

import json
from typing import Optional, Dict, Any, Union, List
from calimero_client_py_bindings import (
    create_connection,
    create_client,
    Client,
    ClientError,
)

from .types import (
    # Admin types
    AdminApiResponse,
    CreateContextRequest,
    CreateContextResponse,
    ListContextsResponse,
    GetContextResponse,
    DeleteContextResponse,
    GenerateIdentityResponse,
    ListIdentitiesResponse,
    InstallDevApplicationRequest,
    InstallApplicationRequest,
    InstallApplicationResponse,
    ListApplicationsResponse,
    GetApplicationResponse,
    UninstallApplicationResponse,
    UploadBlobRequest,
    UploadBlobResponse,
    DownloadBlobResponse,
    ListBlobsResponse,
    GetBlobInfoResponse,
    DeleteBlobResponse,
    UpdateContextApplicationResponse,
    GetContextStorageResponse,
    GetContextValueResponse,
    GetContextStorageEntriesResponse,
    GetProxyContractResponse,
    GrantCapabilitiesResponse,
    RevokeCapabilitiesResponse,
    GetProposalsResponse,
    GetProposalResponse,
    GetNumberOfActiveProposalsResponse,
    GetProposalApprovalsCountResponse,
    GetProposalApproversResponse,
    CreateAliasResponse,
    LookupAliasResponse,
    ListAliasesResponse,
    DeleteAliasResponse,
    HealthCheckResponse,
    IsAuthenticatedResponse,
    GetPeersResponse,
    GetPeersCountResponse,
    GetCertificateResponse,
    SyncContextResponse,
    # JSON-RPC types
    JsonRpcRequest,
    JsonRpcExecuteRequest,
    JsonRpcResponse,
    JsonRpcErrorInfo,
    JsonRpcApiResponse,
    ErrorResponse,
    InviteToContextRequest,
    JoinContextRequest,
    UpdateContextApplicationRequest,
    GetContextStorageEntriesRequest,
    GrantCapabilitiesRequest,
    RevokeCapabilitiesRequest,
    GetProposalsRequest,
    CreateAliasRequest,
    InviteToContextResponse,
    JoinContextResponse,
    SuccessResponse,
)


class CalimeroClient:
    """
    Unified Calimero client that wraps the Rust implementation.

    This client provides a comprehensive interface to the Calimero backend
    with better performance and more features than the previous implementation.
    """

    def __init__(
        self, base_url: str, context_id: str = None, executor_public_key: str = None
    ):
        """
        Initialize the unified Calimero client.

        Args:
            base_url: The base URL of the Calimero node (e.g., "http://localhost:2528").
            context_id: Optional context ID for JSON-RPC operations.
            executor_public_key: Optional public key of the executor for JSON-RPC operations.
        """
        self.base_url = base_url.rstrip("/")
        self.context_id = context_id
        self.executor_public_key = executor_public_key

        # Create connection and client
        self.connection = create_connection(self.base_url)
        self._client = create_client(self.connection)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # The Rust client handles its own cleanup
        pass

    # ============================================================================
    # JSON-RPC Methods
    # ============================================================================

    async def execute(self, method: str, args: Optional[Dict[str, Any]] = None):
        """
        Execute a JSON-RPC method using the Rust client.

        Args:
            method: The method to call.
            args: Optional arguments for the method.

        Returns:
            The JSON-RPC response.

        Raises:
            ValueError: If the request fails or returns an error.
        """
        if not self.context_id or not self.executor_public_key:
            raise ValueError(
                "Context ID and executor public key must be set for JSON-RPC operations"
            )

        try:
            # Convert args to JSON string if provided
            args_json = json.dumps(args) if args else "{}"

            result = self._client.execute_jsonrpc(
                context_id=self.context_id,
                method=method,
                args_json=args_json,
                executor_public_key=self.executor_public_key,
            )

            # Convert the result to match expected format
            return {"jsonrpc": "2.0", "id": 1, "result": result}
        except Exception as e:
            raise ValueError(f"JSON-RPC execution failed: {str(e)}")

    # ============================================================================
    # Context Management
    # ============================================================================

    async def create_context(
        self,
        application_id: str,
        protocol: str = "near",
        initialization_params: List[Any] = None,
    ):
        """Create a new context."""
        try:
            # Convert initialization_params to JSON string if provided
            params = (
                json.dumps(initialization_params) if initialization_params else None
            )

            # The new bindings expect: create_context(app_id, protocol, params)
            result = self._client.create_context(application_id, protocol, params)

            # The new bindings return structured response
            if isinstance(result, dict) and "data" in result:
                data = result["data"]
                context_id = data.get("contextId", "")
                member_public_key = data.get("memberPublicKey", "")
            else:
                context_id = result if isinstance(result, str) else ""
                member_public_key = ""

            return CreateContextResponse(
                success=True,
                context_id=context_id,
                application_id=application_id,
                protocol=protocol,
                member_public_key=member_public_key,
                timestamp=None,
                data={"contextId": context_id, "memberPublicKey": member_public_key},
            )
        except Exception as e:
            return CreateContextResponse(
                success=False,
                context_id="",
                application_id=application_id,
                protocol=protocol,
                member_public_key="",
                timestamp=None,
                data={},
            )

    async def list_contexts(self):
        """List all contexts."""
        try:
            contexts = self._client.list_contexts()

            # Convert to expected format
            context_list = []
            for ctx in contexts:
                context_list.append(
                    {
                        "id": ctx.get("id", ""),
                        "application_id": ctx.get("application_id", ""),
                        "protocol": ctx.get("protocol", ""),
                        "status": ctx.get("status", ""),
                        "created_at": ctx.get("created_at"),
                        "member_count": ctx.get("member_count"),
                    }
                )

            return ListContextsResponse(
                success=True, contexts=context_list, timestamp=None
            )
        except Exception as e:
            return ListContextsResponse(
                success=False, contexts=[], timestamp=None, total_count=0
            )

    async def get_context(self, context_id: str):
        """Get context information."""
        try:
            context = self._client.get_context(context_id)

            return GetContextResponse(success=True, data=context, timestamp=None)
        except Exception as e:
            return GetContextResponse(success=False, data={}, timestamp=None)

    async def delete_context(self, context_id):
        """Delete a context."""
        try:
            self._client.delete_context(context_id)

            return DeleteContextResponse(
                success=True, data={"contextId": context_id}, timestamp=None
            )
        except Exception as e:
            return DeleteContextResponse(success=False, data={}, timestamp=None)

    # ============================================================================
    # Identity Management
    # ============================================================================

    async def generate_identity(self):
        """Generate a new identity."""
        try:
            # The Rust client has generate_context_identity, not generate_identity
            result = self._client.generate_context_identity()

            # The Rust client returns {'data': {'publicKey': '...'}}
            if (
                isinstance(result, dict)
                and "data" in result
                and "publicKey" in result["data"]
            ):
                public_key = result["data"]["publicKey"]
            else:
                public_key = result if isinstance(result, str) else ""

            return GenerateIdentityResponse(
                success=True,
                public_key=public_key,
                context_id=None,
                timestamp=None,
                data={"publicKey": public_key},
            )
        except Exception as e:
            return GenerateIdentityResponse(
                success=False,
                public_key="",
                context_id=None,
                endpoint=None,
                timestamp=None,
                data={},
            )

    async def list_identities(self, context_id: str):
        """List identities in a context."""
        try:
            identities = self._client.get_context_identities(context_id)

            return ListIdentitiesResponse(
                success=True, data={"identities": identities}, timestamp=None
            )
        except Exception as e:
            return ListIdentitiesResponse(success=False, data={}, timestamp=None)

    # ============================================================================
    # Application Management
    # ============================================================================

    async def install_dev_application(self, path: str, metadata: bytes = b""):
        """Install a development application."""
        try:
            result = self._client.install_dev_application(path, metadata)

            return InstallDevApplicationResponse(
                success=True, application_id=result, path="", timestamp=None
            )
        except Exception as e:
            return InstallDevApplicationResponse(
                success=False, application_id="", path="", timestamp=None
            )

    async def install_application(
        self, url: str, hash: str = None, metadata: bytes = b""
    ):
        """Install an application from URL."""
        try:
            # The Rust client expects individual parameters, not a dictionary
            result = self._client.install_application(url, hash, metadata)

            # The Rust client returns {'data': {'applicationId': '...'}}
            if (
                isinstance(result, dict)
                and "data" in result
                and "applicationId" in result["data"]
            ):
                application_id = result["data"]["applicationId"]
            else:
                application_id = result if isinstance(result, str) else ""

            return InstallApplicationResponse(
                success=True,
                application_id=application_id,
                url=url,
                hash=hash,
                timestamp=None,
                data={"applicationId": application_id},
            )
        except Exception as e:
            return InstallApplicationResponse(
                success=False, application_id="", url="", hash=None, timestamp=None
            )

    async def list_applications(self):
        """List all applications."""
        try:
            result = self._client.list_applications()

            # The Rust client returns {'data': {'apps': [...]}}
            if (
                isinstance(result, dict)
                and "data" in result
                and "apps" in result["data"]
            ):
                applications = result["data"]["apps"]
            else:
                applications = result if isinstance(result, list) else []

            return ListApplicationsResponse(
                success=True,
                applications=applications,
                timestamp=None,
                total_count=len(applications),
            )
        except Exception as e:
            return ListApplicationsResponse(
                success=False, applications=[], timestamp=None, total_count=0
            )

    async def get_application(self, application_id: str):
        """Get application information."""
        try:
            application = self._client.get_application(application_id)

            return GetApplicationResponse(
                success=True, application=application, timestamp=None
            )
        except Exception as e:
            return GetApplicationResponse(
                success=False, application=None, timestamp=None
            )

    async def uninstall_application(self, application_id: str):
        """Uninstall an application."""
        try:
            self._client.uninstall_application(application_id)

            return UninstallApplicationResponse(
                success=True, uninstalled_application_id=application_id, timestamp=None
            )
        except Exception as e:
            return UninstallApplicationResponse(
                success=False, uninstalled_application_id="", timestamp=None
            )

    # ============================================================================
    # Invitation and Join
    # ============================================================================

    async def invite_to_context(
        self,
        context_id: str,
        granter_id: str,
        grantee_id: str,
        capability: str = "member",
    ):
        """Invite an identity to a context."""
        try:
            # The new bindings expect: invite_to_context(context_id, inviter_id, invitee_id)
            # Note: capability is not a parameter in the new API
            result = self._client.invite_to_context(context_id, granter_id, grantee_id)

            # The new bindings return structured response
            if isinstance(result, dict) and "data" in result:
                # Check if the data contains an 'invitation' field
                if "invitation" in result["data"]:
                    invitation_payload = result["data"]["invitation"]
                else:
                    invitation_payload = result["data"]
            else:
                invitation_payload = result if isinstance(result, str) else ""

            return InviteToContextResponse(
                success=True,
                invitation_payload=invitation_payload,
                invitation=invitation_payload,
                expires_at=None,
                endpoint=None,
                payload_format=None,
                timestamp=None,
                data={"invitation": invitation_payload},
            )
        except Exception as e:
            return InviteToContextResponse(
                success=False,
                invitation_payload="",
                invitation="",
                expires_at=None,
                endpoint=None,
                payload_format=None,
                timestamp=None,
                data={},
            )

    async def join_context(self, context_id: str, invitee_id: str, invitation: str):
        """Join a context using an invitation."""
        try:
            # The new bindings expect: join_context(context_id, invitee_id, invitation_payload)
            # The invitation_payload contains all necessary information (protocol, network, contract_id)
            result = self._client.join_context(context_id, invitee_id, invitation)

            return JoinContextResponse(
                success=True,
                joined_context_id=context_id,
                member_public_key=result,
                timestamp=None,
                data={"joinedContextId": context_id, "memberPublicKey": result},
            )
        except Exception as e:
            return JoinContextResponse(
                success=False,
                joined_context_id=context_id,
                member_public_key="",
                timestamp=None,
                data={},
            )

    # ============================================================================
    # System Management
    # ============================================================================

    async def get_peers_count(self):
        """Get peer count."""
        try:
            count = self._client.get_peers_count()

            return GetPeersCountResponse(
                success=True, peers_count=count, timestamp=None
            )
        except Exception as e:
            return GetPeersCountResponse(success=False, peers_count=0, timestamp=None)

    async def sync_context(self):
        """Synchronize contexts."""
        try:
            result = self._client.sync_context()

            return SyncContextResponse(success=True, data=result, timestamp=None)
        except Exception as e:
            return SyncContextResponse(success=False, data={}, timestamp=None)

    # ============================================================================
    # New Methods from Rust Client
    # ============================================================================

    async def create_alias(self, alias_type: str, alias_value: str, target_id: str):
        """Create an alias."""
        try:
            result = self._client.create_alias(alias_type, alias_value, target_id)
            return CreateAliasResponse(
                success=True,
                alias=alias_type,
                value=alias_value,
                target_id=target_id,
                timestamp=None,
            )
        except Exception as e:
            return CreateAliasResponse(
                success=False, alias="", value="", target_id="", timestamp=None
            )

    async def delete_alias(self, alias_type: str, alias_value: str):
        """Delete an alias."""
        try:
            self._client.delete_alias(alias_type, alias_value)
            return DeleteAliasResponse(
                success=True,
                deleted_alias_type=alias_type,
                deleted_alias_value=alias_value,
                timestamp=None,
            )
        except Exception as e:
            return DeleteAliasResponse(
                success=False,
                deleted_alias_type="",
                deleted_alias_value="",
                timestamp=None,
            )

    async def lookup_alias(self, alias_type: str, alias_value: str):
        """Lookup an alias."""
        try:
            result = self._client.lookup_alias(alias_type, alias_value)
            return LookupAliasResponse(
                success=True,
                alias=alias_type,
                value=alias_value,
                target_id=result,
                timestamp=None,
            )
        except Exception as e:
            return LookupAliasResponse(
                success=False, alias="", value="", target_id="", timestamp=None
            )

    async def resolve_alias(self, alias_type: str, alias_value: str):
        """Resolve an alias."""
        try:
            result = self._client.resolve_alias(alias_type, alias_value)
            return LookupAliasResponse(
                success=True,
                alias=alias_type,
                value=alias_value,
                target_id=result,
                timestamp=None,
            )
        except Exception as e:
            return LookupAliasResponse(
                success=False, alias="", value="", target_id="", timestamp=None
            )

    async def list_aliases(self):
        """List all aliases."""
        try:
            result = self._client.list_aliases()
            return ListAliasesResponse(
                success=True,
                aliases=result,
                total_count=len(result) if result else 0,
                timestamp=None,
            )
        except Exception as e:
            return ListAliasesResponse(
                success=False, aliases=[], total_count=0, timestamp=None
            )

    async def get_supported_alias_types(self):
        """Get supported alias types."""
        try:
            result = self._client.get_supported_alias_types()
            # Since there's no specific response type, we'll use a generic one
            return SuccessResponse(success=True, timestamp=None)
        except Exception as e:
            return SuccessResponse(success=False, timestamp=None)

    async def grant_permissions(
        self, context_id: str, grantee_id: str, permissions: List[str]
    ):
        """Grant permissions to an identity in a context."""
        try:
            # The new bindings expect capability as a JSON string
            # Convert permissions list to JSON string format: [["public_key", "capability"]]
            capability_json = json.dumps(
                [[grantee_id, permissions[0]] if permissions else [grantee_id, ""]]
            )
            result = self._client.grant_permissions(
                context_id, grantee_id, capability_json
            )
            return GrantCapabilitiesResponse(
                success=True,
                context_id=context_id,
                grantee_id=grantee_id,
                capability=permissions[0] if permissions else "",
                timestamp=None,
            )
        except Exception as e:
            return GrantCapabilitiesResponse(
                success=False,
                context_id="",
                grantee_id="",
                capability="",
                timestamp=None,
            )

    async def revoke_permissions(
        self, context_id: str, grantee_id: str, permissions: List[str]
    ):
        """Revoke permissions from an identity in a context."""
        try:
            # The new bindings expect capability as a JSON string
            # Convert permissions list to JSON string format: [["public_key", "capability"]]
            capability_json = json.dumps(
                [[grantee_id, permissions[0]] if permissions else [grantee_id, ""]]
            )
            result = self._client.revoke_permissions(
                context_id, grantee_id, capability_json
            )
            return RevokeCapabilitiesResponse(
                success=True,
                context_id=context_id,
                revoker_id=grantee_id,
                revokee_id=grantee_id,
                capability=permissions[0] if permissions else "",
                timestamp=None,
            )
        except Exception as e:
            return RevokeCapabilitiesResponse(
                success=False,
                context_id="",
                revoker_id="",
                revokee_id="",
                capability="",
                timestamp=None,
            )

    async def get_context_storage(self, context_id: str):
        """Get context storage information."""
        try:
            result = self._client.get_context_storage(context_id)
            return GetContextStorageResponse(
                success=True, context_id=context_id, storage_data=result, timestamp=None
            )
        except Exception as e:
            return GetContextStorageResponse(
                success=False, context_id="", storage_data={}, timestamp=None
            )

    async def get_context_client_keys(self, context_id: str):
        """Get context client keys."""
        try:
            result = self._client.get_context_client_keys(context_id)
            # Since there's no specific response type, we'll use a generic one
            return SuccessResponse(success=True, timestamp=None)
        except Exception as e:
            return SuccessResponse(success=False, timestamp=None)

    async def get_proposal(self, proposal_id: str):
        """Get proposal information."""
        try:
            result = self._client.get_proposal(proposal_id)
            return GetProposalResponse(success=True, proposal=result, timestamp=None)
        except Exception as e:
            return GetProposalResponse(success=False, proposal=None, timestamp=None)

    async def list_proposals(self):
        """List all proposals."""
        try:
            result = self._client.list_proposals()
            return GetProposalsResponse(
                success=True,
                proposals=result,
                total_count=len(result) if result else 0,
                timestamp=None,
            )
        except Exception as e:
            return GetProposalsResponse(
                success=False, proposals=[], total_count=0, timestamp=None
            )

    async def get_proposal_approvers(self, proposal_id: str):
        """Get proposal approvers."""
        try:
            result = self._client.get_proposal_approvers(proposal_id)
            return GetProposalApproversResponse(
                success=True, proposal_id=proposal_id, approvers=result, timestamp=None
            )
        except Exception as e:
            return GetProposalApproversResponse(
                success=False, proposal_id="", approvers=[], timestamp=None
            )

    async def update_context_application(
        self, context_id: str, application_id: str, executor_public_key: str = None
    ):
        """Update context application."""
        try:
            # The new bindings expect: update_context_application(context_id, app_id, executor_public_key)
            # For backward compatibility, use a default executor if not provided
            if executor_public_key is None:
                # Try to get the executor from the client context
                executor_public_key = getattr(self, "executor_public_key", None)
                if executor_public_key is None:
                    raise ValueError(
                        "executor_public_key is required for update_context_application"
                    )

            result = self._client.update_context_application(
                context_id, application_id, executor_public_key
            )
            return UpdateContextApplicationResponse(
                success=True,
                context_id=context_id,
                application_id=application_id,
                timestamp=None,
            )
        except Exception as e:
            return UpdateContextApplicationResponse(
                success=False, context_id="", application_id="", timestamp=None
            )

    # ============================================================================
    # Strongly Typed Methods (Request-based)
    # ============================================================================

    async def create_context_request(self, request: CreateContextRequest):
        """Create a new context using a request object."""
        return await self.create_context(
            application_id=request.application_id,
            protocol=request.protocol,
            initialization_params=request.initialization_params,
        )

    async def invite_to_context_request(self, request: InviteToContextRequest):
        """Invite an identity to a context using a request object."""
        return await self.invite_to_context(
            context_id=request.context_id,
            granter_id=request.inviter_id,
            grantee_id=request.invitee_id,
            capability=request.capability,
        )

    async def join_context_request(self, request: JoinContextRequest):
        """Join a context using a request object."""
        return await self.join_context(
            context_id=request.context_id,
            invitee_id=request.invitee_id,
            invitation=request.invitation,
        )

    async def install_dev_application_request(
        self, request: InstallDevApplicationRequest
    ):
        """Install a development application using a request object."""
        return await self.install_dev_application(
            path=request.path, metadata=request.metadata
        )

    async def install_application_request(self, request: InstallApplicationRequest):
        """Install an application using a request object."""
        return await self.install_application(
            url=request.url, hash=request.hash, metadata=request.metadata
        )

    async def upload_blob_request(self, request: UploadBlobRequest):
        """Upload a blob using a request object."""
        # Note: This method doesn't exist in the Rust client yet, but we can add it
        # For now, we'll raise NotImplementedError
        raise NotImplementedError("Upload blob not yet implemented in Rust client")

    async def update_context_application_request(
        self, request: UpdateContextApplicationRequest
    ):
        """Update context application using a request object."""
        return await self.update_context_application(
            context_id=request.context_id, application_id=request.application_id
        )

    async def get_context_storage_entries_request(
        self, request: GetContextStorageEntriesRequest
    ):
        """Get context storage entries using a request object."""
        # Note: This method doesn't exist in the Rust client yet
        raise NotImplementedError(
            "Get context storage entries not yet implemented in Rust client"
        )

    async def grant_capabilities_request(self, request: GrantCapabilitiesRequest):
        """Grant capabilities using a request object."""
        return await self.grant_permissions(
            context_id=request.context_id,
            grantee_id=request.grantee_id,
            permissions=request.capabilities,
        )

    async def revoke_capabilities_request(self, request: RevokeCapabilitiesRequest):
        """Revoke capabilities using a request object."""
        return await self.revoke_permissions(
            context_id=request.context_id,
            grantee_id=request.grantee_id,
            permissions=request.capabilities,
        )

    async def get_proposals_request(self, request: GetProposalsRequest):
        """Get proposals using a request object."""
        # Note: This method doesn't exist in the Rust client yet
        raise NotImplementedError(
            "Get proposals with filters not yet implemented in Rust client"
        )

    async def create_alias_request(self, request: CreateAliasRequest):
        """Create an alias using a request object."""
        return await self.create_alias(
            alias_type=request.alias_type,
            alias_value=request.alias_value,
            target_id=request.target_id,
        )

    async def execute_jsonrpc_request(self, request: JsonRpcExecuteRequest):
        """Execute JSON-RPC using a request object."""
        return await self.execute(method=request.method, args=request.args_json)

    # ============================================================================
    # Convenience Methods
    # ============================================================================

    def set_context(self, context_id: str):
        """Set the context ID for JSON-RPC operations."""
        self.context_id = context_id
        return self

    def set_executor(self, executor_public_key: str):
        """Set the executor public key for JSON-RPC operations."""
        self.executor_public_key = executor_public_key
        return self

    def get_context_id(self) -> Optional[str]:
        """Get the current context ID."""
        return self.context_id

    def get_executor_public_key(self) -> Optional[str]:
        """Get the current executor public key."""
        return self.executor_public_key

    def has_context(self) -> bool:
        """Check if the client has a context ID."""
        return self.context_id is not None

    def has_executor(self) -> bool:
        """Check if the client has an executor public key."""
        return self.executor_public_key is not None

    def can_execute(self) -> bool:
        """Check if the client can execute JSON-RPC methods."""
        return self.has_context() and self.has_executor()

    def get_api_url(self) -> str:
        """Get the API URL."""
        return self._client.get_api_url()

    # ============================================================================
    # Compatibility Aliases
    # ============================================================================

    # For backward compatibility
    async def invite(
        self,
        context_id: str,
        granter_id: str,
        grantee_id: str,
        capability: str = "member",
    ):
        """Alias for invite_to_context for backward compatibility."""
        return await self.invite_to_context(
            context_id, granter_id, grantee_id, capability
        )

    # ============================================================================
    # Manager Access (for advanced usage)
    # ============================================================================

    @property
    def contexts(self):
        """Access to context management operations."""
        return ContextManager(self)

    @property
    def identities(self):
        """Access to identity management operations."""
        return IdentityManager(self)

    @property
    def applications(self):
        """Access to application management operations."""
        return ApplicationManager(self)

    @property
    def blobs(self):
        """Access to blob management operations."""
        return BlobManager(self)

    @property
    def capabilities(self):
        """Access to capability management operations."""
        return CapabilityManager(self)

    @property
    def proposals(self):
        """Access to proposal management operations."""
        return ProposalManager(self)

    @property
    def aliases(self):
        """Access to alias management operations."""
        return AliasManager(self)

    @property
    def system(self):
        """Access to system management operations."""
        return SystemManager(self)


# Manager classes for backward compatibility
class ContextManager:
    def __init__(self, client: CalimeroClient):
        self.client = client

    async def create_context(
        self,
        application_id: str,
        protocol: str = "near",
        initialization_params: list = None,
    ):
        return await self.client.create_context(
            application_id, protocol, initialization_params
        )

    async def create_context_request(self, request: CreateContextRequest):
        """Create a new context using a request object."""
        return await self.client.create_context_request(request)

    async def list_contexts(self):
        return await self.client.list_contexts()

    async def get_context(self, context_id: str):
        return await self.client.get_context(context_id)

    async def delete_context(self, context_id: str):
        return await self.client.delete_context(context_id)

    async def invite_to_context(
        self,
        context_id: str,
        granter_id: str,
        grantee_id: str,
        capability: str = "member",
    ):
        return await self.client.invite_to_context(
            context_id, granter_id, grantee_id, capability
        )

    async def invite_to_context_request(self, request: InviteToContextRequest):
        """Invite an identity to a context using a request object."""
        return await self.client.invite_to_context_request(request)

    async def join_context(self, context_id: str, invitee_id: str, invitation: str):
        return await self.client.join_context(context_id, invitee_id, invitation)

    async def join_context_request(self, request: JoinContextRequest):
        """Join a context using a request object."""
        return await self.client.join_context_request(request)

    async def grant_capability(self, context_id: str, grantee_id: str, capability: str):
        return await self.client.grant_permissions(context_id, grantee_id, [capability])

    async def revoke_capability(
        self, context_id: str, grantee_id: str, capability: str
    ):
        return await self.client.revoke_permissions(
            context_id, grantee_id, [capability]
        )


class IdentityManager:
    def __init__(self, client: CalimeroClient):
        self.client = client

    async def generate_identity(self):
        return await self.client.generate_identity()

    async def list_identities(self, context_id: str):
        return await self.client.list_identities(context_id)


class ApplicationManager:
    def __init__(self, client: CalimeroClient):
        self.client = client

    async def install_dev_application(self, path: str, metadata: bytes = b""):
        return await self.client.install_dev_application(path, metadata)

    async def install_dev_application_request(
        self, request: InstallDevApplicationRequest
    ):
        """Install a development application using a request object."""
        return await self.client.install_dev_application_request(request)

    async def install_application(
        self, url: str, hash: str = None, metadata: bytes = b""
    ):
        return await self.client.install_application(url, hash, metadata)

    async def install_application_request(self, request: InstallApplicationRequest):
        """Install an application using a request object."""
        return await self.client.install_application_request(request)

    async def list_applications(self):
        return await self.client.list_applications()

    async def get_application(self, application_id: str):
        return await self.client.get_application(application_id)

    async def uninstall_application(self, application_id: str):
        return await self.client.uninstall_application(application_id)


class BlobManager:
    def __init__(self, client: CalimeroClient):
        self.client = client

    async def get_blob_info(self, blob_id: str):
        return await self.client.get_blob_info(blob_id)

    async def list_blobs(self):
        return await self.client.list_blobs()

    async def delete_blob(self, blob_id: str):
        return await self.client.delete_blob(blob_id)


class CapabilityManager:
    def __init__(self, client: CalimeroClient):
        self.client = client

    async def grant_capability(self, context_id: str, grantee_id: str, capability: str):
        return await self.client.grant_permissions(context_id, grantee_id, [capability])

    async def grant_capability_request(self, request: GrantCapabilitiesRequest):
        """Grant capabilities using a request object."""
        return await self.client.grant_capabilities_request(request)

    async def revoke_capability(
        self, context_id: str, grantee_id: str, capability: str
    ):
        return await self.client.revoke_permissions(
            context_id, grantee_id, [capability]
        )

    async def revoke_capability_request(self, request: RevokeCapabilitiesRequest):
        """Revoke capabilities using a request object."""
        return await self.client.revoke_capabilities_request(request)


class ProposalManager:
    def __init__(self, client: CalimeroClient):
        self.client = client

    async def get_proposal(self, proposal_id: str):
        return await self.client.get_proposal(proposal_id)

    async def list_proposals(self):
        return await self.client.list_proposals()

    async def get_proposal_approvers(self, proposal_id: str):
        return await self.client.get_proposal_approvers(proposal_id)


class AliasManager:
    def __init__(self, client: CalimeroClient):
        self.client = client

    async def create_alias(self, alias_type: str, alias_value: str, target_id: str):
        return await self.client.create_alias(alias_type, alias_value, target_id)

    async def create_alias_request(self, request: CreateAliasRequest):
        """Create an alias using a request object."""
        return await self.client.create_alias_request(request)

    async def delete_alias(self, alias_type: str, alias_value: str):
        return await self.client.delete_alias(alias_type, alias_value)

    async def lookup_alias(self, alias_type: str, alias_value: str):
        return await self.client.lookup_alias(alias_type, alias_value)

    async def resolve_alias(self, alias_type: str, alias_value: str):
        return await self.client.resolve_alias(alias_type, alias_value)

    async def list_aliases(self):
        return await self.client.list_aliases()

    async def get_supported_alias_types(self):
        return await self.client.get_supported_alias_types()


class SystemManager:
    def __init__(self, client: CalimeroClient):
        self.client = client

    async def get_peers_count(self):
        return await self.client.get_peers_count()

    async def sync_context(self):
        return await self.client.sync_context()


# Export the main class
__all__ = ["CalimeroClient"]
