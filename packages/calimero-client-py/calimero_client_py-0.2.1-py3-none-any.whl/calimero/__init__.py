"""
Calimero Network Python Client SDK
"""

__version__ = "0.2.1"


from .ws_subscriptions_client import WsSubscriptionsClient
from .client import CalimeroClient

# Backward compatibility: AdminClient is now an alias for CalimeroClient
# This is needed for the merobox framework that expects AdminClient
AdminClient = CalimeroClient

__all__ = [
    "WsSubscriptionsClient",
    "CalimeroClient",
    "AdminClient",  # Backward compatibility for merobox framework
]
