"""
Strongly typed Request and Response classes for Calimero clients.
This module provides comprehensive type definitions for all API operations.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class MeroboxCompatibleMixin:
    """Mixin to make Pydantic responses compatible with Merobox framework."""

    def __getitem__(self, key):
        # Map Merobox keys to Pydantic field names
        key_mapping = {
            "applicationId": "application_id",
            "contextId": "context_id",
            "memberPublicKey": "member_public_key",
            "inviterId": "inviter_id",
            "inviteeId": "invitee_id",
            "invitation": "invitation",  # Map to invitation field, not invitation_payload
            "granterId": "granter_id",
            "granteeId": "grantee_id",
            "revokerId": "revoker_id",
            "revokeeId": "revokee_id",
            "alias": "alias",
            "value": "value",
        }
        mapped_key = key_mapping.get(key, key)
        return getattr(self, mapped_key)

    def __setitem__(self, key, value):
        # Map Merobox keys to Pydantic field names
        key_mapping = {
            "applicationId": "application_id",
            "contextId": "context_id",
            "memberPublicKey": "member_public_key",
            "inviterId": "inviter_id",
            "inviteeId": "invitee_id",
            "invitation": "invitation",  # Map to invitation field, not invitation_payload
            "granterId": "granter_id",
            "granteeId": "grantee_id",
            "revokerId": "revoker_id",
            "revokeeId": "revokee_id",
            "alias": "alias",
            "value": "value",
        }
        mapped_key = key_mapping.get(key, key)
        setattr(self, mapped_key, value)

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default

    def __contains__(self, key):
        try:
            _ = self[key]
            return True
        except (KeyError, AttributeError):
            return False


# Base class that combines Pydantic and Merobox compatibility
class MeroboxCompatibleModel(BaseModel, MeroboxCompatibleMixin):
    pass


class Capability(str, Enum):
    """Capability types for context operations."""

    MANAGE_APPLICATION = "ManageApplication"
    MANAGE_MEMBERS = "ManageMembers"
    PROXY = "Proxy"
    MEMBER = "member"


# ============================================================================
# Base Classes
# ============================================================================


class BaseRequest(BaseModel):
    """Base class for all request models."""

    model_config = ConfigDict(extra="forbid")


class BaseResponse(BaseModel):
    """Base class for all response models."""

    model_config = ConfigDict(extra="forbid", frozen=False)


class ErrorResponse(BaseResponse):
    """Standard error response format."""

    success: bool = Field(default=False, description="Always false for error responses")
    error: str = Field(description="Error message")
    error_code: Optional[str] = Field(default=None, description="Optional error code")
    timestamp: Optional[datetime] = Field(
        default=None, description="When the error occurred"
    )


class SuccessResponse(BaseResponse):
    """Standard success response format."""

    success: bool = Field(default=True, description="Always true for success responses")
    timestamp: Optional[datetime] = Field(
        default=None, description="When the response was generated"
    )


# ============================================================================
# Admin API Request/Response Classes
# ============================================================================


class CreateContextRequest(BaseRequest):
    """Request to create a new context."""

    application_id: str = Field(
        description="The ID of the application to run in the context"
    )
    protocol: str = Field(
        default="near", description="The protocol to use for the context"
    )
    initialization_params: List[Any] = Field(
        default_factory=list, description="Optional initialization parameters"
    )


class CreateContextResponse(SuccessResponse, MeroboxCompatibleMixin):
    """Response from creating a context."""

    context_id: str = Field(description="The ID of the created context")
    application_id: str = Field(
        description="The ID of the application running in the context"
    )
    protocol: str = Field(description="The protocol used by the context")
    member_public_key: str = Field(description="The public key of the context member")
    timestamp: Optional[datetime] = Field(
        default=None, description="When the context was created"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context data for Merobox compatibility"
    )


class ContextInfo(BaseModel):
    """Information about a context."""

    id: str = Field(description="Context ID")
    application_id: str = Field(description="Application ID running in the context")
    protocol: str = Field(description="Protocol used by the context")
    status: str = Field(description="Current status of the context")
    created_at: Optional[datetime] = Field(
        default=None, description="When the context was created"
    )
    member_count: Optional[int] = Field(
        default=None, description="Number of members in the context"
    )


class ListContextsResponse(SuccessResponse):
    """Response from listing contexts."""

    contexts: List[ContextInfo] = Field(description="List of contexts")
    total_count: int = Field(description="Total number of contexts")


class GetContextResponse(SuccessResponse):
    """Response from getting a specific context."""

    context: ContextInfo = Field(description="Context information")


class DeleteContextResponse(SuccessResponse):
    """Response from deleting a context."""

    deleted_context_id: str = Field(description="ID of the deleted context")


class GenerateIdentityResponse(SuccessResponse, MeroboxCompatibleMixin):
    """Response from generating a new identity."""

    public_key: str = Field(description="The new identity public key")
    context_id: Optional[str] = Field(
        default=None, description="Context ID if generated in a context"
    )
    endpoint: Optional[str] = Field(
        default=None, description="Endpoint for the generated identity"
    )
    timestamp: Optional[datetime] = Field(
        default=None, description="When the identity was generated"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional identity data for Merobox compatibility"
    )


class IdentityInfo(BaseModel):
    """Information about an identity."""

    public_key: str = Field(description="Identity public key")
    context_id: Optional[str] = Field(
        default=None, description="Context ID if part of a context"
    )
    capabilities: List[str] = Field(
        default_factory=list, description="Capabilities of the identity"
    )
    created_at: Optional[datetime] = Field(
        default=None, description="When the identity was created"
    )


class ListIdentitiesResponse(SuccessResponse):
    """Response from listing identities."""

    identities: List[IdentityInfo] = Field(description="List of identities")
    total_count: int = Field(description="Total number of identities")


class InviteToContextRequest(BaseRequest):
    """Request to invite an identity to a context."""

    context_id: str = Field(description="The ID of the context to invite to")
    inviter_id: str = Field(
        description="The public key of the inviter (context member)"
    )
    invitee_id: str = Field(description="The public key of the identity to invite")


class InviteToContextResponse(SuccessResponse, MeroboxCompatibleMixin):
    """Response from inviting to a context."""

    invitation_payload: str = Field(description="The invitation data/token")
    invitation: Optional[str] = Field(
        default=None, description="The invitation data for workflow compatibility"
    )
    expires_at: Optional[datetime] = Field(
        default=None, description="When the invitation expires"
    )
    endpoint: Optional[str] = Field(
        default=None, description="Endpoint for the invitation"
    )
    payload_format: Optional[str] = Field(
        default=None, description="Format of the invitation payload"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional invitation data for Merobox compatibility"
    )


class JoinContextRequest(BaseRequest):
    """Request to join a context using an invitation."""

    context_id: str = Field(description="The ID of the context to join")
    invitee_id: str = Field(
        description="The public key of the identity joining the context"
    )
    invitation_payload: str = Field(
        description="The invitation data/token to join the context"
    )


class JoinContextResponse(SuccessResponse, MeroboxCompatibleMixin):
    """Response from joining a context."""

    joined_context_id: str = Field(description="ID of the context that was joined")
    member_public_key: str = Field(description="Public key of the new member")
    timestamp: Optional[datetime] = Field(
        default=None, description="When the context was joined"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional join data for Merobox compatibility"
    )


class InstallDevApplicationRequest(BaseRequest):
    """Request to install a development application."""

    path: str = Field(description="The local path to install the application from")
    metadata: bytes = Field(default=b"", description="Application metadata as bytes")


class InstallDevApplicationResponse(SuccessResponse):
    """Response from installing a development application."""

    application_id: str = Field(description="The ID of the installed application")
    path: str = Field(description="The path where the application was installed")


class InstallApplicationRequest(BaseRequest):
    """Request to install an application from URL."""

    url: str = Field(description="The URL to install the application from")
    hash: Optional[str] = Field(
        default=None, description="Optional hash for verification"
    )
    metadata: bytes = Field(default=b"", description="Application metadata as bytes")


class InstallApplicationResponse(SuccessResponse, MeroboxCompatibleMixin):
    """Response from installing an application from URL."""

    application_id: str = Field(description="The ID of the installed application")
    url: str = Field(description="The URL the application was installed from")
    hash: Optional[str] = Field(
        default=None, description="Optional hash of the application"
    )
    timestamp: Optional[datetime] = Field(
        default=None, description="When the installation occurred"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional installation data for Merobox compatibility",
    )


class ApplicationInfo(BaseModel):
    """Information about an application."""

    id: str = Field(description="Application ID")
    name: Optional[str] = Field(default=None, description="Application name")
    version: Optional[str] = Field(default=None, description="Application version")
    status: str = Field(description="Current status of the application")
    installed_at: Optional[datetime] = Field(
        default=None, description="When the application was installed"
    )
    metadata: Optional[bytes] = Field(default=None, description="Application metadata")


class ListApplicationsResponse(SuccessResponse):
    """Response from listing applications."""

    applications: List[ApplicationInfo] = Field(description="List of applications")
    total_count: int = Field(description="Total number of applications")


class GetApplicationResponse(SuccessResponse):
    """Response from getting a specific application."""

    application: ApplicationInfo = Field(description="Application information")


class UninstallApplicationResponse(SuccessResponse):
    """Response from uninstalling an application."""

    uninstalled_application_id: str = Field(
        description="ID of the uninstalled application"
    )


class UploadBlobRequest(BaseRequest):
    """Request to upload a blob."""

    data: bytes = Field(description="The blob data to upload")
    metadata: bytes = Field(default=b"", description="Optional metadata for the blob")


class UploadBlobResponse(SuccessResponse):
    """Response from uploading a blob."""

    blob_id: str = Field(description="The ID of the uploaded blob")
    size: int = Field(description="Size of the uploaded blob in bytes")


class BlobInfo(BaseModel):
    """Information about a blob."""

    id: str = Field(description="Blob ID")
    size: int = Field(description="Size of the blob in bytes")
    metadata: Optional[bytes] = Field(default=None, description="Blob metadata")
    uploaded_at: Optional[datetime] = Field(
        default=None, description="When the blob was uploaded"
    )


class DownloadBlobResponse(SuccessResponse):
    """Response from downloading a blob."""

    blob: BlobInfo = Field(description="Blob information")
    data: bytes = Field(description="The blob data")


class ListBlobsResponse(SuccessResponse):
    """Response from listing blobs."""

    blobs: List[BlobInfo] = Field(description="List of blobs")
    total_count: int = Field(description="Total number of blobs")


class GetBlobInfoResponse(SuccessResponse):
    """Response from getting blob information."""

    blob: BlobInfo = Field(description="Blob information")


class DeleteBlobResponse(SuccessResponse):
    """Response from deleting a blob."""

    deleted_blob_id: str = Field(description="ID of the deleted blob")


class UpdateContextApplicationRequest(BaseRequest):
    """Request to update the application running in a context."""

    context_id: str = Field(description="The ID of the context")
    application_id: str = Field(description="The new application ID")


class UpdateContextApplicationResponse(SuccessResponse):
    """Response from updating a context application."""

    updated_context_id: str = Field(description="ID of the updated context")
    new_application_id: str = Field(description="New application ID")


class ContextStorageEntry(BaseModel):
    """A storage entry in a context."""

    key: str = Field(description="Storage key")
    value: Any = Field(description="Storage value")
    created_at: Optional[datetime] = Field(
        default=None, description="When the entry was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="When the entry was last updated"
    )


class GetContextStorageResponse(SuccessResponse):
    """Response from getting context storage."""

    context_id: str = Field(description="Context ID")
    storage: List[ContextStorageEntry] = Field(description="Storage entries")
    total_count: int = Field(description="Total number of storage entries")


class GetContextValueResponse(SuccessResponse):
    """Response from getting a context storage value."""

    context_id: str = Field(description="Context ID")
    key: str = Field(description="Storage key")
    value: Any = Field(description="Storage value")


class GetContextStorageEntriesRequest(BaseRequest):
    """Request to get storage entries from a context."""

    context_id: str = Field(description="The ID of the context")
    prefix: str = Field(default="", description="Optional prefix to filter keys")
    limit: int = Field(default=100, description="Maximum number of entries to return")


class GetContextStorageEntriesResponse(SuccessResponse):
    """Response from getting context storage entries."""

    context_id: str = Field(description="Context ID")
    entries: List[ContextStorageEntry] = Field(description="Storage entries")
    total_count: int = Field(
        description="Total number of entries matching the criteria"
    )
    has_more: bool = Field(description="Whether there are more entries available")


class GetProxyContractResponse(SuccessResponse):
    """Response from getting a context's proxy contract."""

    context_id: str = Field(description="Context ID")
    proxy_contract: Dict[str, Any] = Field(description="Proxy contract information")


class GrantCapabilitiesRequest(BaseRequest):
    """Request to grant capabilities to a user in a context."""

    context_id: str = Field(description="The ID of the context")
    granter_id: str = Field(description="The public key of the granter")
    grantee_id: str = Field(description="The public key of the grantee")
    capability: str = Field(description="The capability to grant")


class GrantCapabilitiesResponse(SuccessResponse):
    """Response from granting capabilities."""

    context_id: str = Field(description="Context ID")
    grantee_id: str = Field(description="Grantee public key")
    granted_capability: str = Field(description="Granted capability")


class RevokeCapabilitiesRequest(BaseRequest):
    """Request to revoke capabilities from a user in a context."""

    context_id: str = Field(description="The ID of the context")
    revoker_id: str = Field(description="The public key of the revoker")
    revokee_id: str = Field(description="The public key of the revokee")
    capability: str = Field(description="The capability to revoke")


class RevokeCapabilitiesResponse(SuccessResponse):
    """Response from revoking capabilities."""

    context_id: str = Field(description="Context ID")
    revokee_id: str = Field(description="Revokee public key")
    revoked_capability: str = Field(description="Revoked capability")


class ProposalInfo(BaseModel):
    """Information about a proposal."""

    id: str = Field(description="Proposal ID")
    context_id: str = Field(description="Context ID")
    proposer_id: str = Field(description="Proposer public key")
    status: str = Field(description="Current status of the proposal")
    created_at: Optional[datetime] = Field(
        default=None, description="When the proposal was created"
    )
    expires_at: Optional[datetime] = Field(
        default=None, description="When the proposal expires"
    )


class GetProposalsRequest(BaseRequest):
    """Request to get proposals for a context."""

    context_id: str = Field(description="The ID of the context")
    offset: int = Field(default=0, description="The offset for pagination")
    limit: int = Field(
        default=100, description="The maximum number of proposals to return"
    )


class GetProposalsResponse(SuccessResponse):
    """Response from getting proposals."""

    context_id: str = Field(description="Context ID")
    proposals: List[ProposalInfo] = Field(description="List of proposals")
    total_count: int = Field(description="Total number of proposals")
    has_more: bool = Field(description="Whether there are more proposals available")


class GetProposalResponse(SuccessResponse):
    """Response from getting a specific proposal."""

    proposal: ProposalInfo = Field(description="Proposal information")


class GetNumberOfActiveProposalsResponse(SuccessResponse):
    """Response from getting the number of active proposals."""

    context_id: str = Field(description="Context ID")
    active_proposals_count: int = Field(description="Number of active proposals")


class GetProposalApprovalsCountResponse(SuccessResponse):
    """Response from getting proposal approval count."""

    context_id: str = Field(description="Context ID")
    proposal_id: str = Field(description="Proposal ID")
    approvals_count: int = Field(description="Number of approvals")


class GetProposalApproversResponse(SuccessResponse):
    """Response from getting proposal approvers."""

    context_id: str = Field(description="Context ID")
    proposal_id: str = Field(description="Proposal ID")
    approvers: List[str] = Field(description="List of approver public keys")
    total_count: int = Field(description="Total number of approvers")


class CreateAliasRequest(BaseRequest):
    """Base request for creating aliases."""

    alias: str = Field(description="The alias name")
    value: Dict[str, Any] = Field(description="The value to alias")


class CreateContextAliasRequest(CreateAliasRequest):
    """Request to create a context ID alias."""

    alias: str = Field(description="The alias name")
    context_id: str = Field(description="The context ID to alias")


class CreateApplicationAliasRequest(CreateAliasRequest):
    """Request to create an application ID alias."""

    alias: str = Field(description="The alias name")
    application_id: str = Field(description="The application ID to alias")


class CreateIdentityAliasRequest(CreateAliasRequest):
    """Request to create an identity alias in a context."""

    context_id: str = Field(description="The ID of the context")
    alias: str = Field(description="The alias name")
    identity_id: str = Field(description="The identity to alias")


class CreateAliasResponse(SuccessResponse):
    """Response from creating an alias."""

    alias: str = Field(description="The created alias name")
    value: Dict[str, Any] = Field(description="The aliased value")


class AliasInfo(BaseModel):
    """Information about an alias."""

    name: str = Field(description="Alias name")
    value: Dict[str, Any] = Field(description="Aliased value")
    created_at: Optional[datetime] = Field(
        default=None, description="When the alias was created"
    )


class LookupAliasResponse(SuccessResponse):
    """Response from looking up an alias."""

    alias: AliasInfo = Field(description="Alias information")


class ListAliasesResponse(SuccessResponse):
    """Response from listing aliases."""

    aliases: List[AliasInfo] = Field(description="List of aliases")
    total_count: int = Field(description="Total number of aliases")


class DeleteAliasResponse(SuccessResponse):
    """Response from deleting an alias."""

    deleted_alias: str = Field(description="Name of the deleted alias")


class HealthCheckResponse(SuccessResponse):
    """Response from health check."""

    status: str = Field(description="Health status")
    uptime: Optional[float] = Field(
        default=None, description="Server uptime in seconds"
    )
    version: Optional[str] = Field(default=None, description="Server version")


class IsAuthenticatedResponse(SuccessResponse):
    """Response from authentication check."""

    authenticated: bool = Field(description="Whether the session is authenticated")
    user_id: Optional[str] = Field(default=None, description="User ID if authenticated")


class PeerInfo(BaseModel):
    """Information about a peer."""

    id: str = Field(description="Peer ID")
    address: str = Field(description="Peer address")
    status: str = Field(description="Peer connection status")
    connected_at: Optional[datetime] = Field(
        default=None, description="When the peer connected"
    )


class GetPeersResponse(SuccessResponse):
    """Response from getting peer information."""

    peers: List[PeerInfo] = Field(description="List of peers")
    total_count: int = Field(description="Total number of peers")


class GetPeersCountResponse(SuccessResponse):
    """Response from getting peer count."""

    peers_count: int = Field(description="Number of connected peers")


class GetCertificateResponse(SuccessResponse):
    """Response from getting server certificate."""

    certificate: str = Field(description="Server certificate data")
    expires_at: Optional[datetime] = Field(
        default=None, description="When the certificate expires"
    )


class SyncContextResponse(SuccessResponse):
    """Response from syncing a context."""

    context_id: Optional[str] = Field(
        default=None, description="Context ID that was synced"
    )
    synced_at: datetime = Field(description="When the sync was completed")


# ============================================================================
# JSON-RPC Request/Response Classes
# ============================================================================


class JsonRpcRequest(BaseRequest):
    """JSON-RPC request format."""

    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: int = Field(description="Request ID")
    method: str = Field(description="Method to call")
    params: Dict[str, Any] = Field(description="Method parameters")


class JsonRpcExecuteRequest(BaseRequest):
    """JSON-RPC execute request parameters."""

    context_id: str = Field(description="Context ID for the request")
    method: str = Field(description="Method to execute")
    args_json: Dict[str, Any] = Field(
        default_factory=dict, description="Method arguments as JSON"
    )
    executor_public_key: str = Field(description="Public key of the executor")
    timeout: int = Field(default=1000, description="Request timeout in milliseconds")


class JsonRpcErrorInfo(BaseModel):
    """JSON-RPC error information."""

    code: int = Field(description="Error code")
    message: str = Field(description="Error message")
    data: Optional[Any] = Field(default=None, description="Additional error data")


class JsonRpcResponse(BaseResponse):
    """JSON-RPC response format."""

    jsonrpc: str = Field(description="JSON-RPC version")
    id: int = Field(description="Request ID")
    result: Optional[Any] = Field(default=None, description="Method result")
    error: Optional[JsonRpcErrorInfo] = Field(
        default=None, description="Error information"
    )


# ============================================================================
# WebSocket Request/Response Classes
# ============================================================================


class WebSocketMessage(BaseModel):
    """Base WebSocket message format."""

    type: str = Field(description="Message type")
    data: Any = Field(description="Message data")


class SubscribeRequest(BaseRequest):
    """Request to subscribe to application updates."""

    application_ids: List[str] = Field(
        description="List of application IDs to subscribe to"
    )


class UnsubscribeRequest(BaseRequest):
    """Request to unsubscribe from application updates."""

    application_ids: List[str] = Field(
        description="List of application IDs to unsubscribe from"
    )


class SubscriptionUpdate(BaseModel):
    """Update from a subscription."""

    application_id: str = Field(description="Application ID")
    event_type: str = Field(description="Type of event")
    data: Any = Field(description="Event data")
    timestamp: datetime = Field(description="When the event occurred")


# ============================================================================
# Union Types for Generic Responses
# ============================================================================

# Admin API response types
AdminApiResponse = Union[
    CreateContextResponse,
    ListContextsResponse,
    GetContextResponse,
    DeleteContextResponse,
    GenerateIdentityResponse,
    ListIdentitiesResponse,
    InviteToContextResponse,
    JoinContextResponse,
    InstallDevApplicationResponse,
    InstallApplicationResponse,
    ListApplicationsResponse,
    GetApplicationResponse,
    UninstallApplicationResponse,
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
    ErrorResponse,
]

# JSON-RPC response types
JsonRpcApiResponse = Union[JsonRpcResponse, ErrorResponse]

# WebSocket response types
WebSocketApiResponse = Union[WebSocketMessage, SubscriptionUpdate, ErrorResponse]
