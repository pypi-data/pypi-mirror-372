"""
Basic functionality tests for Calimero client without workflow dependencies.
"""

import pytest
from calimero import CalimeroClient
from calimero.types import Capability


def test_basic_imports():
    """Test that basic imports work correctly."""
    assert CalimeroClient is not None
    assert Capability is not None


def test_capability_enum():
    """Test that capability enum values are correct."""
    assert Capability.MANAGE_APPLICATION == "ManageApplication"
    assert Capability.MANAGE_MEMBERS == "ManageMembers"
    assert Capability.PROXY == "Proxy"
    assert Capability.MEMBER == "member"


def test_client_instantiation():
    """Test that client can be instantiated with basic parameters."""
    client = CalimeroClient(base_url="http://localhost:2528")
    assert client is not None
    assert hasattr(client, "base_url")
    assert client.base_url == "http://localhost:2528"


def test_types_import():
    """Test that types module can be imported and used."""
    from calimero.types import BaseRequest, BaseResponse

    assert BaseRequest is not None
    assert BaseResponse is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
