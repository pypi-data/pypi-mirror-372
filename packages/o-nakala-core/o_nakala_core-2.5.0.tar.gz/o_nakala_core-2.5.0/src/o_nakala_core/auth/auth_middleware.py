"""
Authentication middleware for CLI and web interfaces.
Provides unified authentication handling across all O-Nakala Core components.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import jwt

from .institutional_auth import InstitutionalAuthManager, UserProfile, InstitutionalRole
from .session_manager import SessionManager
from ..common.config import NakalaConfig

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Authentication-related errors."""

    pass


class AuthorizationError(Exception):
    """Authorization-related errors."""

    pass


class AuthMiddleware:
    """Authentication middleware for CLI and web interfaces."""

    def __init__(self, config: NakalaConfig = None):
        self.config = config or NakalaConfig()
        self.institutional_auth = InstitutionalAuthManager()
        self.session_manager = SessionManager()
        self.jwt_secret = self._get_or_create_jwt_secret()

    def _get_or_create_jwt_secret(self) -> str:
        """Get or create JWT secret for session tokens."""
        secret_path = os.path.expanduser("~/.nakala/jwt_secret")

        if os.path.exists(secret_path):
            with open(secret_path, "r") as f:
                return f.read().strip()
        else:
            # Generate new secret
            import secrets

            secret = secrets.token_urlsafe(32)

            os.makedirs(os.path.dirname(secret_path), exist_ok=True)
            with open(secret_path, "w") as f:
                f.write(secret)

            # Secure the file
            os.chmod(secret_path, 0o600)
            return secret

    def authenticate_cli(
        self, api_key: str = None, institution: str = None, user_id: str = None
    ) -> UserProfile:
        """
        Authenticate CLI request.

        Args:
            api_key: NAKALA API key or institutional API key
            institution: Institution identifier for SSO
            user_id: User identifier for session lookup

        Returns:
            UserProfile if authentication successful

        Raises:
            AuthenticationError: If authentication fails
        """
        # Method 1: Direct NAKALA API key
        if api_key and not institution:
            # Check if it's an institutional API key
            user_profile = self.institutional_auth.get_user_by_api_key(api_key)
            if user_profile:
                return user_profile

            # For direct NAKALA API keys, create minimal profile
            return UserProfile(
                user_id=f"nakala_{hashlib.md5(api_key.encode()).hexdigest()[:8]}",
                email="",
                name="NAKALA API User",
                institution="external",
                institutional_roles=[InstitutionalRole.RESEARCHER],
                api_key=api_key,
            )

        # Method 2: Institutional authentication
        if institution and user_id:
            user_profile = self.institutional_auth._load_user_profile(user_id)
            if user_profile and user_profile.institution == institution:
                return user_profile

        # Method 3: Environment variables
        env_api_key = os.getenv("NAKALA_API_KEY")
        if env_api_key:
            return self.authenticate_cli(api_key=env_api_key)

        # Method 4: Saved session
        if user_id:
            session = self.session_manager.get_session(user_id)
            if session and session.is_valid():
                user_profile = self.institutional_auth._load_user_profile(user_id)
                if user_profile:
                    return user_profile

        raise AuthenticationError("No valid authentication method found")

    def authenticate_web(
        self, request_headers: Dict[str, str], cookies: Dict[str, str] = None
    ) -> UserProfile:
        """
        Authenticate web request.

        Args:
            request_headers: HTTP request headers
            cookies: HTTP cookies

        Returns:
            UserProfile if authentication successful

        Raises:
            AuthenticationError: If authentication fails
        """
        # Method 1: Authorization header with Bearer token
        auth_header = request_headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            user_profile = self._validate_jwt_token(token)
            if user_profile:
                return user_profile

        # Method 2: API key header
        api_key = request_headers.get("X-API-KEY") or request_headers.get("X-Api-Key")
        if api_key:
            return self.authenticate_cli(api_key=api_key)

        # Method 3: Session cookie
        if cookies:
            session_token = cookies.get("nakala_session")
            if session_token:
                user_profile = self._validate_session_cookie(session_token)
                if user_profile:
                    return user_profile

        raise AuthenticationError("No valid authentication found in request")

    def _validate_jwt_token(self, token: str) -> Optional[UserProfile]:
        """Validate JWT token and return user profile."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])

            user_id = payload.get("user_id")
            institution = payload.get("institution")

            if user_id and institution:
                user_profile = self.institutional_auth._load_user_profile(user_id)
                if user_profile and user_profile.institution == institution:
                    # Check token expiration
                    exp = payload.get("exp", 0)
                    if datetime.fromtimestamp(exp) > datetime.now():
                        return user_profile

        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")

        return None

    def _validate_session_cookie(self, session_token: str) -> Optional[UserProfile]:
        """Validate session cookie and return user profile."""
        try:
            # Decode session token (could be JWT or session ID)
            if "." in session_token:  # Looks like JWT
                return self._validate_jwt_token(session_token)
            else:
                # Session ID lookup
                session = self.session_manager.get_session_by_token(session_token)
                if session and session.is_valid():
                    return self.institutional_auth._load_user_profile(session.user_id)

        except Exception as e:
            logger.warning(f"Session validation error: {e}")

        return None

    def create_jwt_token(
        self, user_profile: UserProfile, expires_in: int = 3600
    ) -> str:
        """Create JWT token for user."""
        payload = {
            "user_id": user_profile.user_id,
            "email": user_profile.email,
            "name": user_profile.name,
            "institution": user_profile.institution,
            "roles": [role.value for role in user_profile.institutional_roles],
            "iat": datetime.now().timestamp(),
            "exp": (datetime.now() + timedelta(seconds=expires_in)).timestamp(),
        }

        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def require_auth(
        self, required_roles: list = None, required_permissions: list = None
    ):
        """
        Decorator for requiring authentication.

        Args:
            required_roles: List of required institutional roles
            required_permissions: List of required permissions
        """

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract authentication context based on function type
                user_profile = None

                # For CLI functions - look for api_key or auth context in kwargs
                if "api_key" in kwargs:
                    try:
                        user_profile = self.authenticate_cli(api_key=kwargs["api_key"])
                    except AuthenticationError:
                        raise AuthenticationError("CLI authentication required")

                # For web functions - look for request object or headers
                elif "request" in kwargs:
                    request = kwargs["request"]
                    try:
                        user_profile = self.authenticate_web(
                            request_headers=getattr(request, "headers", {}),
                            cookies=getattr(request, "cookies", {}),
                        )
                    except AuthenticationError:
                        raise AuthenticationError("Web authentication required")

                if not user_profile:
                    raise AuthenticationError("Authentication required")

                # Check role requirements
                if required_roles:
                    user_role_values = [
                        role.value for role in user_profile.institutional_roles
                    ]
                    if not any(role in user_role_values for role in required_roles):
                        raise AuthorizationError(f"Required roles: {required_roles}")

                # Check permission requirements
                if required_permissions:
                    for permission in required_permissions:
                        if not self.institutional_auth.validate_user_permissions(
                            user_profile, permission
                        ):
                            raise AuthorizationError(
                                f"Permission required: {permission}"
                            )

                # Add user profile to function context
                kwargs["user_profile"] = user_profile

                return func(*args, **kwargs)

            return wrapper

        return decorator

    def require_institutional_auth(self, institutions: list = None):
        """
        Decorator for requiring institutional authentication.

        Args:
            institutions: List of allowed institutions
        """

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user_profile = kwargs.get("user_profile")

                if not user_profile:
                    # Try to authenticate first
                    try:
                        if "api_key" in kwargs:
                            user_profile = self.authenticate_cli(
                                api_key=kwargs["api_key"]
                            )
                        elif "request" in kwargs:
                            request = kwargs["request"]
                            user_profile = self.authenticate_web(
                                request_headers=getattr(request, "headers", {}),
                                cookies=getattr(request, "cookies", {}),
                            )
                    except AuthenticationError:
                        raise AuthenticationError(
                            "Institutional authentication required"
                        )

                if not user_profile:
                    raise AuthenticationError("Institutional authentication required")

                # Check if user belongs to allowed institutions
                if institutions and user_profile.institution not in institutions:
                    raise AuthorizationError(
                        f"Institution not allowed. Allowed: {institutions}"
                    )

                # Ensure user has institutional context (not just API key)
                if user_profile.institution == "external":
                    raise AuthorizationError(
                        "Institutional authentication required (API key not sufficient)"
                    )

                kwargs["user_profile"] = user_profile
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def get_user_context(
        self, api_key: str = None, request_headers: Dict[str, str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get user context for logging and analytics.

        Returns basic user information without sensitive data.
        """
        try:
            user_profile = None

            if api_key:
                user_profile = self.authenticate_cli(api_key=api_key)
            elif request_headers:
                user_profile = self.authenticate_web(request_headers)

            if user_profile:
                return {
                    "user_id": user_profile.user_id,
                    "institution": user_profile.institution,
                    "roles": [role.value for role in user_profile.institutional_roles],
                    "authenticated_at": datetime.now().isoformat(),
                }

        except AuthenticationError:
            pass

        return None

    def log_user_activity(
        self,
        user_profile: UserProfile,
        action: str,
        resource: str = None,
        metadata: Dict[str, Any] = None,
    ):
        """Log user activity for audit trail."""
        activity_log = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_profile.user_id,
            "institution": user_profile.institution,
            "action": action,
            "resource": resource,
            "metadata": metadata or {},
        }

        # Log to file
        log_path = os.path.expanduser("~/.nakala/activity.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        with open(log_path, "a") as f:
            f.write(json.dumps(activity_log) + "\n")

        logger.info(f"User activity: {user_profile.user_id} - {action}")


# Convenience functions for common authentication patterns
def require_researcher_role(func: Callable):
    """Require researcher role or higher."""
    auth = AuthMiddleware()
    return auth.require_auth(required_roles=["researcher", "professor", "admin"])(func)


def require_admin_role(func: Callable):
    """Require admin role."""
    auth = AuthMiddleware()
    return auth.require_auth(required_roles=["admin"])(func)


def require_collection_permissions(func: Callable):
    """Require permissions to manage collections."""
    auth = AuthMiddleware()
    return auth.require_auth(
        required_permissions=["create_collection", "modify_metadata"]
    )(func)


def require_upload_permissions(func: Callable):
    """Require permissions to upload data."""
    auth = AuthMiddleware()
    return auth.require_auth(required_permissions=["upload_data"])(func)


def require_research_auth(func: Callable):
    """Require research institution authentication."""
    auth = AuthMiddleware()
    return auth.require_institutional_auth(institutions=["example_research"])(func)


def require_library_auth(func: Callable):
    """Require library institutional authentication."""
    auth = AuthMiddleware()
    return auth.require_institutional_auth(institutions=["example_library"])(func)
