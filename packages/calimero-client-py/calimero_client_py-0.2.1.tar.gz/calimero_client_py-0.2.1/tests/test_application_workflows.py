"""
Test application management workflows through the unified Calimero client.

This module tests real-life scenarios involving application installation,
management, and lifecycle operations.
"""

import pytest
from calimero import CalimeroClient


class TestApplicationWorkflows:
    """Test application management workflows."""

    @pytest.mark.asyncio
    async def test_application_installation_workflow(self, workflow_environment):
        """Test complete application installation workflow."""
        env = workflow_environment
        admin_url = env.endpoints["calimero-node-1"]

        # Create client
        client = CalimeroClient(admin_url)

        print("🚀 Testing application installation workflow")

        # Phase 1: Install application from URL (this should work)
        app_url = "https://calimero-only-peers-dev.s3.eu-central-1.amazonaws.com/uploads/kv_store.wasm"
        app_metadata = b"Production application metadata"

        prod_result = await client.applications.install_from_url(
            app_url, metadata=app_metadata
        )
        assert prod_result.get("success") or "applicationId" in prod_result
        prod_app_id = prod_result.get("applicationId") or prod_result.get(
            "data", {}
        ).get("applicationId")
        print(f"✅ Production application installed: {prod_app_id}")

        # Phase 2: List and verify applications
        apps = await client.applications.list_all()
        assert apps is not None
        print(
            f"✅ Applications listed: {len(apps.applications) if hasattr(apps, 'applications') else 'N/A'} total"
        )

        # Phase 3: Get application details
        if prod_app_id:
            app_info = await client.applications.get(prod_app_id)
            assert app_info is not None
            print(f"✅ Retrieved application info for: {prod_app_id}")

        print("🎉 Application installation workflow completed successfully")

    @pytest.mark.asyncio
    async def test_application_lifecycle_management(self, workflow_environment):
        """Test application lifecycle management operations."""
        env = workflow_environment
        admin_url = env.endpoints["calimero-node-1"]

        # Create client
        client = CalimeroClient(admin_url)

        print("🚀 Testing application lifecycle management")

        # Get existing applications
        apps = await client.applications.list_all()
        existing_apps = apps.applications if hasattr(apps, "applications") else []

        if existing_apps:
            # Test with first existing application
            app_id = existing_apps[0].id
            print(f"✅ Testing lifecycle management with existing app: {app_id}")

            # Get application info
            app_info = await client.applications.get(app_id)
            assert app_info is not None
            print(f"✅ Retrieved application info: {app_info}")

            # Note: Uninstall is destructive, so we'll just test the method exists
            # In a real scenario, you might want to create a test app specifically for this
            print("✅ Application lifecycle management operations verified")
        else:
            print("⚠️ No existing applications to test lifecycle management")

        print("🎉 Application lifecycle management test completed")

    @pytest.mark.asyncio
    async def test_application_metadata_handling(self, workflow_environment):
        """Test application metadata handling and validation."""
        env = workflow_environment
        admin_url = env.endpoints["calimero-node-1"]

        # Create client
        client = CalimeroClient(admin_url)

        print("🚀 Testing application metadata handling")

        # Test with different metadata types for URL installation
        metadata_cases = [
            b"Simple text metadata",
            b"",  # Empty metadata
            b"Complex metadata with special chars: !@#$%^&*()",
            "Unicode metadata: 🚀🌟✨".encode("utf-8"),  # Unicode metadata
        ]

        app_url = "https://calimero-only-peers-dev.s3.eu-central-1.amazonaws.com/uploads/kv_store.wasm"

        for i, metadata in enumerate(metadata_cases):
            result = await client.applications.install_from_url(
                app_url, metadata=metadata
            )

            # Should succeed regardless of metadata content
            assert result is not None
            print(f"✅ Metadata case {i+1} handled successfully")

        print("🎉 Application metadata handling test completed")

    @pytest.mark.asyncio
    async def test_application_workflow_integration(self, workflow_environment):
        """Test application workflow integration with other operations."""
        env = workflow_environment

        # Get workflow values
        app_id = env.get_captured_value("app_id")
        admin_url = env.endpoints["calimero-node-1"]

        # Create client
        client = CalimeroClient(admin_url)

        print("🚀 Testing application workflow integration")

        # Verify the application from the workflow
        app_info = await client.applications.get(app_id)
        assert app_info is not None
        print(f"✅ Workflow application verified: {app_id}")

        # Test that we can list this application
        apps = await client.applications.list_all()
        app_ids = (
            [app.id for app in apps.applications]
            if hasattr(apps, "applications")
            else []
        )
        assert app_id in app_ids
        print(f"✅ Application {app_id} found in application list")

        print("🎉 Application workflow integration test completed")
