"""
AZTP (Astha Zero Trust Platform) Client Library for Python
"""

from aztp_client.client import Aztp
from aztp_client.common.types import SecuredAgent, Identity
from aztp_client.common.config import whiteListTrustDomains

__version__ = "0.1.0"
__all__ = ["Aztp", "SecuredAgent", "Identity", "whiteListTrustDomains"] 