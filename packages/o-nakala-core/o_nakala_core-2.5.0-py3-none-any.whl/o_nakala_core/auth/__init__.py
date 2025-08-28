"""
Authentication and authorization module for O-Nakala Core.
Provides SSO, institutional authentication, and user management.
"""

from .sso_provider import SSOProvider, SAMLProvider, OAuthProvider
from .institutional_auth import InstitutionalAuthManager
from .user_manager import UserManager, UserProfile, InstitutionalRole
from .auth_middleware import AuthMiddleware
from .session_manager import SessionManager

__all__ = [
    "SSOProvider",
    "SAMLProvider",
    "OAuthProvider",
    "InstitutionalAuthManager",
    "UserManager",
    "UserProfile",
    "InstitutionalRole",
    "AuthMiddleware",
    "SessionManager",
]
