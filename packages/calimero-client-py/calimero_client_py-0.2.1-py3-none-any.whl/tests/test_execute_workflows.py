"""
Test JSON-RPC execute workflows through the unified Calimero client.

This module tests real-life scenarios involving JSON-RPC method execution,
including key-value operations, context management, and executor setup.
"""

import pytest
from calimero import CalimeroClient


class TestExecuteWorkflows:
    """Test JSON-RPC execute workflows."""

    @pytest.mark.asyncio
    async def test_basic_key_value_operations(self, workflow_environment):
        """Test basic key-value operations through JSON-RPC."""
        env = workflow_environment

        # Get workflow values
        context_id = env.get_captured_value("context_id")
        executor_public_key = env.get_captured_value("member_public_key")
        admin_url = env.endpoints["calimero-node-1"]

        # Create client configured for JSON-RPC
        client = CalimeroClient(
            base_url=admin_url,
            context_id=context_id,
            executor_public_key=executor_public_key,
        )

        print("🚀 Testing basic key-value operations")

        # Test set operations
        test_data = [
            ("test_key_1", "test_value_1"),
            ("test_key_2", "test_value_2"),
            ("test_key_3", "test_value_3"),
        ]

        for key, value in test_data:
            set_result = await client.execute("set", [key, value])
            assert set_result.get("result", {}).get("output") is None
            print(f"✅ Set '{key}' = '{value}'")

        # Test get operations
        for key, expected_value in test_data:
            get_result = await client.execute("get", [key])
            retrieved_value = get_result.get("result", {}).get("output")
            assert retrieved_value == expected_value
            print(f"✅ Get '{key}' = '{retrieved_value}'")

        print("🎉 Basic key-value operations completed successfully")

    @pytest.mark.asyncio
    async def test_method_chaining_setup(self, workflow_environment):
        """Test method chaining for client setup."""
        env = workflow_environment

        # Get workflow values
        context_id = env.get_captured_value("context_id")
        executor_public_key = env.get_captured_value("member_public_key")
        admin_url = env.endpoints["calimero-node-1"]

        # Create client and use method chaining
        client = CalimeroClient(admin_url)
        client.set_context(context_id).set_executor(executor_public_key)

        # Verify setup
        assert client.get_context_id() == context_id
        assert client.get_executor_public_key() == executor_public_key
        assert client.can_execute()

        print("✅ Method chaining setup completed successfully")

        # Test execution after chaining
        result = await client.execute("set", ["chained_key", "chained_value"])
        assert result.get("result", {}).get("output") is None
        print("✅ JSON-RPC execution after chained setup successful")

    @pytest.mark.asyncio
    async def test_execute_with_invalid_context(self, workflow_environment):
        """Test execute operations with invalid context setup."""
        env = workflow_environment
        admin_url = env.endpoints["calimero-node-1"]

        # Create client without context/executor
        client = CalimeroClient(admin_url)

        # Should not be able to execute
        assert not client.can_execute()

        # Attempting to execute should fail
        with pytest.raises(ValueError, match="JSON-RPC error"):
            await client.execute("get", ["test_key"])

        print("✅ Invalid context execution properly handled")

    @pytest.mark.asyncio
    async def test_execute_workflow_integration(self, workflow_environment):
        """Test complete execute workflow integration."""
        env = workflow_environment

        # Get workflow values
        context_id = env.get_captured_value("context_id")
        executor_public_key = env.get_captured_value("member_public_key")
        admin_url = env.endpoints["calimero-node-1"]

        # Create client
        client = CalimeroClient(
            base_url=admin_url,
            context_id=context_id,
            executor_public_key=executor_public_key,
        )

        print("🚀 Testing complete execute workflow integration")

        # Phase 1: Setup and verification
        assert client.can_execute()
        print("✅ Client properly configured for JSON-RPC operations")

        # Phase 2: Data operations
        workflow_data = [
            ("workflow_key_1", "workflow_value_1"),
            ("workflow_key_2", "workflow_value_2"),
            ("workflow_key_3", "workflow_value_3"),
        ]

        for key, value in workflow_data:
            await client.execute("set", [key, value])
            print(f"✅ Set '{key}' = '{value}'")

        # Phase 3: Verification and cleanup
        for key, expected_value in workflow_data:
            result = await client.execute("get", [key])
            retrieved_value = result.get("result", {}).get("output")
            assert retrieved_value == expected_value
            print(f"✅ Verified '{key}' = '{expected_value}'")

        print("🎉 Complete execute workflow integration successful")
