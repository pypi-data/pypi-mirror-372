"""
SSO Provider implementations for SAML and OAuth2 institutional authentication.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import requests
from urllib.parse import urlencode
import base64
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


@dataclass
class AuthenticationResult:
    """Result of authentication attempt."""

    success: bool
    user_id: str
    email: str
    name: str
    institution: str
    roles: List[str]
    attributes: Dict[str, Any]
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None


class SSOProvider(ABC):
    """Abstract base class for SSO providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = config.get("name", "unknown")

    @abstractmethod
    def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate authentication URL for user redirect."""
        pass

    @abstractmethod
    def handle_callback(self, callback_data: Dict[str, Any]) -> AuthenticationResult:
        """Handle authentication callback and extract user information."""
        pass

    @abstractmethod
    def validate_token(self, token: str) -> AuthenticationResult:
        """Validate an existing authentication token."""
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> AuthenticationResult:
        """Refresh an expired access token."""
        pass


class SAMLProvider(SSOProvider):
    """SAML 2.0 authentication provider for institutional SSO."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.entity_id = config.get("entity_id")
        self.sso_url = config.get("sso_url")
        self.certificate = config.get("certificate")
        self.attribute_map = config.get("attribute_map", {})

        # Default SAML attribute mappings for common institutions
        self.default_attribute_map = {
            "user_id": [
                "urn:oid:0.9.2342.19200300.100.1.1",
                "uid",
                "eduPersonPrincipalName",
            ],
            "email": ["urn:oid:0.9.2342.19200300.100.1.3", "mail", "email"],
            "name": ["urn:oid:2.5.4.3", "cn", "displayName"],
            "institution": [
                "urn:oid:1.3.6.1.4.1.5923.1.1.1.3",
                "schacHomeOrganization",
                "o",
            ],
            "roles": [
                "urn:oid:1.3.6.1.4.1.5923.1.1.1.1",
                "eduPersonAffiliation",
                "memberOf",
            ],
        }

    def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate SAML authentication URL."""
        saml_request = self._build_saml_request(redirect_uri)
        encoded_request = base64.b64encode(saml_request.encode()).decode()

        params = {"SAMLRequest": encoded_request, "RelayState": state or redirect_uri}

        return f"{self.sso_url}?{urlencode(params)}"

    def handle_callback(self, callback_data: Dict[str, Any]) -> AuthenticationResult:
        """Handle SAML response and extract user attributes."""
        try:
            saml_response = callback_data.get("SAMLResponse")
            if not saml_response:
                return AuthenticationResult(
                    success=False,
                    user_id="",
                    email="",
                    name="",
                    institution="",
                    roles=[],
                    attributes={},
                    error_message="Missing SAML response",
                )

            # Decode and parse SAML response
            decoded_response = base64.b64decode(saml_response).decode()
            attributes = self._parse_saml_response(decoded_response)

            # Map attributes to user profile
            user_profile = self._map_attributes(attributes)

            return AuthenticationResult(
                success=True,
                user_id=user_profile.get("user_id", ""),
                email=user_profile.get("email", ""),
                name=user_profile.get("name", ""),
                institution=user_profile.get("institution", ""),
                roles=user_profile.get("roles", []),
                attributes=attributes,
            )

        except Exception as e:
            logger.error(f"SAML callback error: {e}")
            return AuthenticationResult(
                success=False,
                user_id="",
                email="",
                name="",
                institution="",
                roles=[],
                attributes={},
                error_message=str(e),
            )

    def validate_token(self, token: str) -> AuthenticationResult:
        """SAML doesn't use tokens, return invalid result."""
        return AuthenticationResult(
            success=False,
            user_id="",
            email="",
            name="",
            institution="",
            roles=[],
            attributes={},
            error_message="SAML does not support token validation",
        )

    def refresh_token(self, refresh_token: str) -> AuthenticationResult:
        """SAML doesn't use refresh tokens."""
        return AuthenticationResult(
            success=False,
            user_id="",
            email="",
            name="",
            institution="",
            roles=[],
            attributes={},
            error_message="SAML does not support token refresh",
        )

    def _build_saml_request(self, redirect_uri: str) -> str:
        """Build SAML authentication request."""
        request_id = f"_nakala_{datetime.now().timestamp()}"
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        saml_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                    ID="{request_id}"
                    Version="2.0"
                    IssueInstant="{timestamp}"
                    Destination="{self.sso_url}"
                    AssertionConsumerServiceURL="{redirect_uri}"
                    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
    <saml:Issuer>{self.entity_id}</saml:Issuer>
</samlp:AuthnRequest>"""

        return saml_request

    def _parse_saml_response(self, saml_response: str) -> Dict[str, Any]:
        """Parse SAML response and extract attributes."""
        try:
            root = ET.fromstring(saml_response)
            attributes = {}

            # Find attribute statements
            for attr_stmt in root.findall(
                ".//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement"
            ):
                for attr in attr_stmt.findall(
                    ".//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"
                ):
                    attr_name = attr.get("Name")
                    attr_values = []

                    for value in attr.findall(
                        ".//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue"
                    ):
                        if value.text:
                            attr_values.append(value.text)

                    if attr_values:
                        attributes[attr_name] = (
                            attr_values[0] if len(attr_values) == 1 else attr_values
                        )

            return attributes

        except ET.ParseError as e:
            logger.error(f"SAML response parsing error: {e}")
            return {}

    def _map_attributes(self, saml_attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Map SAML attributes to user profile fields."""
        user_profile = {}

        for field, possible_attrs in self.default_attribute_map.items():
            # Check custom mapping first
            if field in self.attribute_map:
                custom_attr = self.attribute_map[field]
                if custom_attr in saml_attributes:
                    user_profile[field] = saml_attributes[custom_attr]
                    continue

            # Check default mappings
            for attr_name in possible_attrs:
                if attr_name in saml_attributes:
                    user_profile[field] = saml_attributes[attr_name]
                    break

        return user_profile


class OAuthProvider(SSOProvider):
    """OAuth 2.0 authentication provider for institutional SSO."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.auth_url = config.get("auth_url")
        self.token_url = config.get("token_url")
        self.userinfo_url = config.get("userinfo_url")
        self.scope = config.get("scope", "openid profile email")

    def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": self.scope,
            "redirect_uri": redirect_uri,
            "state": state or "",
        }

        return f"{self.auth_url}?{urlencode(params)}"

    def handle_callback(self, callback_data: Dict[str, Any]) -> AuthenticationResult:
        """Handle OAuth callback and exchange code for tokens."""
        try:
            auth_code = callback_data.get("code")
            redirect_uri = callback_data.get("redirect_uri", "")

            if not auth_code:
                return AuthenticationResult(
                    success=False,
                    user_id="",
                    email="",
                    name="",
                    institution="",
                    roles=[],
                    attributes={},
                    error_message="Missing authorization code",
                )

            # Exchange code for tokens
            token_data = self._exchange_code_for_tokens(auth_code, redirect_uri)
            if not token_data.get("access_token"):
                return AuthenticationResult(
                    success=False,
                    user_id="",
                    email="",
                    name="",
                    institution="",
                    roles=[],
                    attributes={},
                    error_message="Failed to obtain access token",
                )

            # Get user information
            user_info = self._get_user_info(token_data["access_token"])

            expires_at = None
            if token_data.get("expires_in"):
                expires_at = datetime.now() + timedelta(
                    seconds=int(token_data["expires_in"])
                )

            return AuthenticationResult(
                success=True,
                user_id=user_info.get("sub", user_info.get("id", "")),
                email=user_info.get("email", ""),
                name=user_info.get("name", user_info.get("display_name", "")),
                institution=user_info.get(
                    "organization", user_info.get("institution", "")
                ),
                roles=user_info.get("roles", []),
                attributes=user_info,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_at=expires_at,
            )

        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            return AuthenticationResult(
                success=False,
                user_id="",
                email="",
                name="",
                institution="",
                roles=[],
                attributes={},
                error_message=str(e),
            )

    def validate_token(self, token: str) -> AuthenticationResult:
        """Validate OAuth access token."""
        try:
            user_info = self._get_user_info(token)

            return AuthenticationResult(
                success=True,
                user_id=user_info.get("sub", user_info.get("id", "")),
                email=user_info.get("email", ""),
                name=user_info.get("name", user_info.get("display_name", "")),
                institution=user_info.get(
                    "organization", user_info.get("institution", "")
                ),
                roles=user_info.get("roles", []),
                attributes=user_info,
                access_token=token,
            )

        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return AuthenticationResult(
                success=False,
                user_id="",
                email="",
                name="",
                institution="",
                roles=[],
                attributes={},
                error_message=str(e),
            )

    def refresh_token(self, refresh_token: str) -> AuthenticationResult:
        """Refresh OAuth access token."""
        try:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            response = requests.post(self.token_url, data=data)
            response.raise_for_status()

            token_data = response.json()

            # Get updated user information
            user_info = self._get_user_info(token_data["access_token"])

            expires_at = None
            if token_data.get("expires_in"):
                expires_at = datetime.now() + timedelta(
                    seconds=int(token_data["expires_in"])
                )

            return AuthenticationResult(
                success=True,
                user_id=user_info.get("sub", user_info.get("id", "")),
                email=user_info.get("email", ""),
                name=user_info.get("name", user_info.get("display_name", "")),
                institution=user_info.get(
                    "organization", user_info.get("institution", "")
                ),
                roles=user_info.get("roles", []),
                attributes=user_info,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token", refresh_token),
                expires_at=expires_at,
            )

        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return AuthenticationResult(
                success=False,
                user_id="",
                email="",
                name="",
                institution="",
                roles=[],
                attributes={},
                error_message=str(e),
            )

    def _exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        return response.json()

    def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information using access token."""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.userinfo_url, headers=headers)
        response.raise_for_status()

        return response.json()


class InstitutionalSSOFactory:
    """Factory for creating institutional SSO providers."""

    # Pre-configured institutional providers
    INSTITUTION_CONFIGS = {
        "example_research": {
            "name": "Example Research Institution",
            "type": "saml",
            "entity_id": "https://nakala.example-research.org",
            "sso_url": "https://idp.example-research.org/simplesaml/saml2/idp/SSOService.php",
            "attribute_map": {
                "user_id": "eduPersonPrincipalName",
                "email": "mail",
                "name": "cn",
                "institution": "schacHomeOrganization",
                "roles": "eduPersonAffiliation",
            },
        },
        "example_library": {
            "name": "Example National Library",
            "type": "oauth",
            "auth_url": "https://auth.example-library.org/oauth2/authorize",
            "token_url": "https://auth.example-library.org/oauth2/token",
            "userinfo_url": "https://auth.example-library.org/oauth2/userinfo",
            "scope": "openid profile email institution",
        },
        "unistra": {
            "name": "Example University",
            "type": "saml",
            "entity_id": "https://nakala.unistra.fr",
            "sso_url": "https://idp.unistra.fr/idp/profile/SAML2/Redirect/SSO",
            "attribute_map": {
                "user_id": "uid",
                "email": "mail",
                "name": "displayName",
                "institution": "o",
                "roles": "memberOf",
            },
        },
        "huma_num": {
            "name": "Huma-Num",
            "type": "oauth",
            "auth_url": "https://auth.huma-num.fr/oauth2/authorize",
            "token_url": "https://auth.huma-num.fr/oauth2/token",
            "userinfo_url": "https://auth.huma-num.fr/oauth2/userinfo",
            "scope": "openid profile email organization",
        },
    }

    @classmethod
    def create_provider(
        cls, institution: str, custom_config: Dict[str, Any] = None
    ) -> SSOProvider:
        """Create SSO provider for institution."""
        config = cls.INSTITUTION_CONFIGS.get(institution.lower())

        if not config:
            if custom_config:
                config = custom_config
            else:
                raise ValueError(f"Unknown institution: {institution}")

        # Merge custom config if provided
        if custom_config:
            config.update(custom_config)

        provider_type = config.get("type", "oauth")

        if provider_type == "saml":
            return SAMLProvider(config)
        elif provider_type == "oauth":
            return OAuthProvider(config)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    @classmethod
    def list_supported_institutions(cls) -> List[str]:
        """List supported institutional providers."""
        return list(cls.INSTITUTION_CONFIGS.keys())
