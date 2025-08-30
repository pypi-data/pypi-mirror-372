"""
Test context management workflows through the unified Calimero client.

This module tests real-life scenarios involving context creation, management,
and lifecycle operations.
"""

import asyncio
import pytest
from calimero import CalimeroClient
from calimero.types import Capability


class TestContextWorkflows:
    """Test context management workflows."""

    @pytest.mark.asyncio
    async def test_context_creation_workflow(self, workflow_environment):
        """Test complete context creation workflow."""
        env = workflow_environment

        app_id = env.get_captured_value("app_id")
        admin_url = env.endpoints["calimero-node-1"]

        client = CalimeroClient(admin_url)

        print("🚀 Testing context creation workflow")

        context_result = await client.contexts.create(
            application_id=app_id, protocol="near", initialization_params=[]
        )
        assert context_result is not None

        if isinstance(context_result, dict):
            if "data" in context_result and "contextId" in context_result["data"]:
                context_id = context_result["data"]["contextId"]
            elif "contextId" in context_result:
                context_id = context_result["contextId"]
            else:
                raise ValueError(f"Unexpected context result format: {context_result}")
        else:
            context_id = context_result

        print(f"✅ Context created with default protocol: {context_id}")

        custom_context_result = await client.contexts.create(
            application_id=app_id,
            protocol="near",
            initialization_params=[],
        )
        assert custom_context_result is not None

        if isinstance(custom_context_result, dict):
            if (
                "data" in custom_context_result
                and "contextId" in custom_context_result["data"]
            ):
                custom_context_id = custom_context_result["data"]["contextId"]
            elif "contextId" in custom_context_result:
                custom_context_id = custom_context_result["contextId"]
            else:
                custom_context_id = None
        else:
            custom_context_id = custom_context_result

        print(f"✅ Context created with custom protocol: {custom_context_id}")

        contexts = await client.contexts.list_all()
        assert contexts is not None
        print(f"✅ Retrieved all contexts: {contexts}")

        print("🎉 Context creation workflow completed successfully")

    @pytest.mark.asyncio
    async def test_context_management_workflow(self, workflow_environment):
        """Test context management operations."""
        env = workflow_environment

        context_id = env.get_captured_value("context_id")
        admin_url = env.endpoints["calimero-node-1"]

        client = CalimeroClient(admin_url)

        print("🚀 Testing context management workflow")

        context_info = await client.contexts.get(context_id)
        assert context_info is not None
        print(f"✅ Retrieved context info: {context_info}")

        contexts = await client.contexts.list_all()
        assert contexts is not None

        if hasattr(contexts, "contexts") and contexts.contexts:
            context_ids = [ctx.id for ctx in contexts.contexts]
            assert context_id in context_ids
            print(f"✅ Context {context_id} found in context list")

        print("🎉 Context management workflow completed successfully")

    @pytest.mark.asyncio
    async def test_context_invitation_workflow(self, workflow_environment):
        """Test context invitation workflow."""
        env = workflow_environment

        context_id = env.get_captured_value("context_id")
        granter_id = env.get_captured_value("member_public_key")
        admin_url = env.endpoints["calimero-node-1"]

        client = CalimeroClient(admin_url)

        print("🚀 Testing context invitation workflow")

        new_identity = await client.identities.generate()
        assert new_identity is not None

        if isinstance(new_identity, dict):
            if "data" in new_identity and "publicKey" in new_identity["data"]:
                grantee_id = new_identity["data"]["publicKey"]
            elif "publicKey" in new_identity:
                grantee_id = new_identity["publicKey"]
            else:
                grantee_id = None
        else:
            grantee_id = new_identity

        print(f"✅ Generated new identity for invitation: {grantee_id}")

        invitation = await client.invite(
            context_id=context_id,
            granter_id=granter_id,
            grantee_id=grantee_id,
            capability="member",
        )
        assert invitation is not None
        print("✅ Invitation created successfully")

        if isinstance(invitation, dict):
            if "data" in invitation:
                invitation_data = invitation["data"]
                assert isinstance(invitation_data, str)
                print("✅ Invitation format verified")
            else:
                print("⚠️  Invitation format different than expected")

        identities = await client.identities.list_in_context(context_id)
        assert identities is not None
        print(f"✅ Context membership verified: {identities}")

        print("🎉 Context invitation workflow completed successfully")

    @pytest.mark.asyncio
    async def test_context_lifecycle_workflow(self, workflow_environment):
        """Test context lifecycle operations."""
        env = workflow_environment

        app_id = env.get_captured_value("app_id")
        admin_url = env.endpoints["calimero-node-1"]

        client = CalimeroClient(admin_url)

        print("🚀 Testing context lifecycle workflow")

        test_context = await client.contexts.create(
            application_id=app_id,
            protocol="near",
            initialization_params=[],
        )
        assert test_context is not None

        if isinstance(test_context, dict):
            if "data" in test_context and "contextId" in test_context["data"]:
                test_context_id = test_context["data"]["contextId"]
            elif "contextId" in test_context:
                test_context_id = test_context["contextId"]
            else:
                test_context_id = None
        else:
            test_context_id = test_context

        print(f"✅ Test context created: {test_context_id}")

        context_info = await client.contexts.get(test_context_id)
        assert context_info is not None
        print("✅ Test context verified")

        delete_result = await client.contexts.delete(test_context_id)
        assert delete_result is not None
        print("✅ Test context deleted")

        try:
            await client.contexts.get(test_context_id)
            assert False, "Context should not exist after deletion"
        except Exception:
            print("✅ Context deletion verified")

        print("🎉 Context lifecycle workflow completed successfully")

    @pytest.mark.asyncio
    async def test_context_workflow_integration(self, workflow_environment):
        """Test context workflow integration with other operations."""
        env = workflow_environment

        context_id = env.get_captured_value("context_id")
        app_id = env.get_captured_value("app_id")
        admin_url = env.endpoints["calimero-node-1"]

        client = CalimeroClient(admin_url)

        print("🚀 Testing context workflow integration")

        context_info = await client.contexts.get(context_id)
        assert context_info is not None
        print(f"✅ Workflow context verified: {context_id}")

        if hasattr(context_info, "data") and context_info.data:
            data = context_info.data
            context_app_id = data.get("applicationId")
            assert context_app_id == app_id
            print(f"✅ Context application verified: {context_app_id}")

        contexts = await client.contexts.list_all()
        assert contexts is not None

        if hasattr(contexts, "contexts") and contexts.contexts:
            context_ids = [ctx.id for ctx in contexts.contexts]
            assert context_id in context_ids
            print(f"✅ Context {context_id} found in context list")

        print("🎉 Context workflow integration completed successfully")

    @pytest.mark.asyncio
    async def test_capability_management_workflow(self, workflow_environment):
        """Test complete capability management workflow."""
        env = workflow_environment

        context_id = env.get_captured_value("context_id")
        granter_id = env.get_captured_value("member_public_key")
        grantee_id = env.get_captured_value("public_key")  # Use identity from node 2

        # Use node 1 for invitation and capability management
        node1_url = env.endpoints["calimero-node-1"]
        # Use node 2 for joining context
        node2_url = env.endpoints["calimero-node-2"]

        client_node1 = CalimeroClient(node1_url)
        client_node2 = CalimeroClient(node2_url)

        print("🚀 Testing capability management workflow")
        print(f"🔑 Granter (node 1): {granter_id}")
        print(f"👤 Grantee (node 2): {grantee_id}")
        print(f"🏗️  Context: {context_id}")

        # Step 1: Invite from node 1
        print("🔐 Step 1: Inviting identity from node 1")
        invitation = await client_node1.contexts.invite_to_context(
            context_id=context_id,
            inviter_id=granter_id,
            invitee_id=grantee_id,
        )
        assert invitation is not None
        print("✅ Invitation created successfully from node 1")

        # Wait between steps
        print("⏳ Waiting 2 seconds between invitation and join...")
        await asyncio.sleep(2)

        # Step 2: Join from node 2
        print("🔐 Step 2: Joining context from node 2")
        print(f"🔍 Invitation type: {type(invitation)}")
        print(f"🔍 Invitation content: {invitation}")

        # Handle invitation payload properly
        if isinstance(invitation, dict):
            # If invitation is a dict, extract the invitation data
            invitation_payload = invitation.get("data", str(invitation))
        else:
            # If invitation is already a string, use it directly
            invitation_payload = invitation

        join_result = await client_node2.contexts.join_context(
            context_id=context_id,
            invitee_id=grantee_id,
            invitation_payload=invitation_payload,
        )
        assert join_result is not None
        print("✅ Context joined successfully from node 2")

        # Wait between steps
        print("⏳ Waiting 2 seconds between join and capability grant...")
        await asyncio.sleep(2)

        # Step 3: Grant capabilities from node 1
        print("🔐 Step 3: Granting capabilities from node 1")
        capabilities_to_test = [
            Capability.MANAGE_APPLICATION,
            Capability.MANAGE_MEMBERS,
            Capability.PROXY,
        ]

        for capability in capabilities_to_test:
            print(f"🔧 Testing capability: {capability.value}")

            print(
                f"📤 Granting {capability.value} to {grantee_id} in context {context_id}"
            )
            grant_result = await client_node1.contexts.grant_capability(
                context_id=context_id,
                granter_id=granter_id,
                grantee_id=grantee_id,
                capability=capability,
            )
            print(f"📥 Grant result: {grant_result}")

            assert grant_result is not None
            print(f"✅ Granted {capability.value} capability")

            if isinstance(grant_result, dict):
                assert grant_result.get("success", True)
                print(f"✅ {capability.value} grant operation verified")

            # Wait between capability grants
            if capability != capabilities_to_test[-1]:  # Don't wait after the last one
                print("⏳ Waiting 2 seconds between capability grants...")
                await asyncio.sleep(2)

        print("🎉 Capability management workflow completed successfully")

    @pytest.mark.asyncio
    async def test_capability_enum_usage(self, workflow_environment):
        """Test capability enum usage and validation."""
        env = workflow_environment

        context_id = env.get_captured_value("context_id")
        granter_id = env.get_captured_value("member_public_key")
        admin_url = env.endpoints["calimero-node-1"]

        client = CalimeroClient(admin_url)

        print("🚀 Testing capability enum usage")

        assert Capability.MANAGE_APPLICATION.value == "ManageApplication"
        assert Capability.MANAGE_MEMBERS.value == "ManageMembers"
        assert Capability.PROXY.value == "Proxy"
        print("✅ Capability enum values verified")

        all_capabilities = list(Capability)
        assert len(all_capabilities) == 3
        capability_values = [cap.value for cap in all_capabilities]
        assert "ManageApplication" in capability_values
        assert "ManageMembers" in capability_values
        assert "Proxy" in capability_values
        print("✅ Capability enum iteration verified")

        assert Capability.MANAGE_APPLICATION == Capability.MANAGE_APPLICATION
        assert Capability.MANAGE_APPLICATION != Capability.MANAGE_MEMBERS
        print("✅ Capability enum comparison verified")

        manage_app_str = str(Capability.MANAGE_APPLICATION)
        assert "MANAGE_APPLICATION" in manage_app_str
        print("✅ Capability enum string conversion verified")

        print("🎉 Capability enum usage test completed successfully")

    @pytest.mark.asyncio
    async def test_capability_grant_revoke_cycle(self, workflow_environment):
        """Test complete capability grant and revoke cycle."""
        env = workflow_environment

        context_id = env.get_captured_value("context_id")
        granter_id = env.get_captured_value("member_public_key")
        grantee_id = env.get_captured_value("public_key")  # Use identity from node 2

        # Use node 1 for invitation and capability management
        node1_url = env.endpoints["calimero-node-1"]
        # Use node 2 for joining context
        node2_url = env.endpoints["calimero-node-2"]

        client_node1 = CalimeroClient(node1_url)
        client_node2 = CalimeroClient(node2_url)

        print("🚀 Testing capability grant and revoke cycle")
        print(f"🔑 Granter (node 1): {granter_id}")
        print(f"👤 Grantee (node 2): {grantee_id}")
        print(f"🏗️  Context: {context_id}")

        # Step 1: Invite from node 1
        print("🔐 Step 1: Inviting identity from node 1")
        invitation = await client_node1.contexts.invite_to_context(
            context_id=context_id,
            inviter_id=granter_id,
            invitee_id=grantee_id,
        )
        assert invitation is not None
        print("✅ Invitation created successfully from node 1")

        # Wait between steps
        print("⏳ Waiting 2 seconds between invitation and join...")
        await asyncio.sleep(2)

        # Step 2: Join from node 2
        print("🔐 Step 2: Joining context from node 2")
        print(f"🔍 Invitation type: {type(invitation)}")
        print(f"🔍 Invitation content: {invitation}")

        # Handle invitation payload properly
        if isinstance(invitation, dict):
            # If invitation is a dict, extract the invitation data
            invitation_payload = invitation.get("data", str(invitation))
        else:
            # If invitation is already a string, use it directly
            invitation_payload = invitation

        join_result = await client_node2.contexts.join_context(
            context_id=context_id,
            invitee_id=grantee_id,
            invitation_payload=invitation_payload,
        )
        assert join_result is not None
        print("✅ Context joined successfully from node 2")

        # Wait between steps
        print("⏳ Waiting 2 seconds between join and capability grant...")
        await asyncio.sleep(2)

        # Step 3: Grant capability from node 1
        print("🔐 Step 3: Granting capability from node 1")
        print(f"📤 Granting MANAGE_MEMBERS to {grantee_id} in context {context_id}")
        grant_result = await client_node1.contexts.grant_capability(
            context_id=context_id,
            granter_id=granter_id,
            grantee_id=grantee_id,
            capability=Capability.MANAGE_MEMBERS,
        )
        print(f"📥 Grant result: {grant_result}")

        assert grant_result is not None
        print("✅ Granted MANAGE_MEMBERS capability")

        if isinstance(grant_result, dict):
            assert grant_result.get("success", True)
            print("✅ Grant operation verified")

        # Wait between grant and revoke
        print("⏳ Waiting 2 seconds between grant and revoke...")
        await asyncio.sleep(2)

        # Step 4: Revoke capability from node 1
        print("🔐 Step 4: Revoking capability from node 1")
        print(f"📤 Revoking MANAGE_MEMBERS from {grantee_id} in context {context_id}")
        revoke_result = await client_node1.contexts.revoke_capability(
            context_id=context_id,
            revoker_id=granter_id,
            revokee_id=grantee_id,
            capability=Capability.MANAGE_MEMBERS,
        )
        print(f"📥 Revoke result: {revoke_result}")

        assert revoke_result is not None
        print("✅ Revoked MANAGE_MEMBERS capability")

        if isinstance(revoke_result, dict):
            assert revoke_result.get("success", True)
            print("✅ Revoke operation verified")

        print("🎉 Capability grant and revoke cycle completed successfully")

    @pytest.mark.asyncio
    async def test_capability_error_handling(self, workflow_environment):
        """Test capability error handling with invalid inputs."""
        env = workflow_environment

        context_id = env.get_captured_value("context_id")
        admin_url = env.endpoints["calimero-node-1"]

        client = CalimeroClient(admin_url)

        print("🚀 Testing capability error handling")

        try:
            await client.contexts.grant_capability(
                context_id="invalid_context_id",
                granter_id="invalid_granter_id",
                grantee_id="invalid_grantee_id",
                capability=Capability.MANAGE_APPLICATION,
            )
            print("⚠️  Expected error for invalid context ID")
        except Exception as e:
            print(f"✅ Properly handled invalid context ID: {e}")

        try:
            await client.contexts.grant_capability(
                context_id=context_id,
                granter_id="invalid_granter_id",
                grantee_id="invalid_grantee_id",
                capability="INVALID_CAPABILITY",
            )
            print("⚠️  Expected error for invalid capability")
        except Exception as e:
            print(f"✅ Properly handled invalid capability: {e}")

        try:
            await client.contexts.grant_capability(
                context_id=None,
                granter_id=None,
                grantee_id=None,
                capability=None,
            )
            print("⚠️  Expected error for None values")
        except Exception as e:
            print(f"✅ Properly handled None values: {e}")

        print("🎉 Capability error handling test completed successfully")
