"""
Services package for external service clients.

This package contains HTTP clients for communicating with external microservices:
- AuthClient: Handles authentication, users, and organizations (Auth service)
- CofreClient: Handles certificate operations (Cofre service)
"""

from backend.app.services.auth_client import auth_client
from backend.app.services.cofre_client import cofre_client

__all__ = ["auth_client", "cofre_client"]
