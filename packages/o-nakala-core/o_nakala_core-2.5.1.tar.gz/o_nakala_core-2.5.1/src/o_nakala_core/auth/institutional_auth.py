"""
Institutional authentication manager for O-Nakala Core.
Handles institution-specific authentication policies and user management.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .sso_provider import SSOProvider, InstitutionalSSOFactory, AuthenticationResult

logger = logging.getLogger(__name__)


class InstitutionalRole(Enum):
    """Standard institutional roles for digital humanities."""

    STUDENT = "student"
    RESEARCHER = "researcher"
    LIBRARIAN = "librarian"
    ARCHIVIST = "archivist"
    PROFESSOR = "professor"
    CURATOR = "curator"
    ADMIN = "admin"
    TECH_SUPPORT = "tech_support"
    GUEST = "guest"


@dataclass
class UserProfile:
    """User profile with institutional context."""

    user_id: str
    email: str
    name: str
    institution: str
    institutional_roles: List[InstitutionalRole] = field(default_factory=list)
    nakala_roles: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    api_key: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_admin(self) -> bool:
        """Check if user has administrative privileges."""
        return InstitutionalRole.ADMIN in self.institutional_roles

    @property
    def is_researcher(self) -> bool:
        """Check if user is a researcher."""
        return InstitutionalRole.RESEARCHER in self.institutional_roles

    @property
    def can_manage_collections(self) -> bool:
        """Check if user can manage collections."""
        return any(
            role in self.institutional_roles
            for role in [
                InstitutionalRole.RESEARCHER,
                InstitutionalRole.LIBRARIAN,
                InstitutionalRole.ARCHIVIST,
                InstitutionalRole.CURATOR,
                InstitutionalRole.PROFESSOR,
                InstitutionalRole.ADMIN,
            ]
        )

    @property
    def can_upload_data(self) -> bool:
        """Check if user can upload data."""
        return any(
            role in self.institutional_roles
            for role in [
                InstitutionalRole.STUDENT,
                InstitutionalRole.RESEARCHER,
                InstitutionalRole.LIBRARIAN,
                InstitutionalRole.ARCHIVIST,
                InstitutionalRole.CURATOR,
                InstitutionalRole.PROFESSOR,
                InstitutionalRole.ADMIN,
            ]
        )


@dataclass
class InstitutionalPolicy:
    """Institution-specific authentication and access policies."""

    institution: str
    require_2fa: bool = False
    allowed_domains: List[str] = field(default_factory=list)
    session_timeout: int = 3600  # seconds
    max_concurrent_sessions: int = 5
    require_institutional_email: bool = True
    auto_provision_users: bool = True
    default_roles: List[InstitutionalRole] = field(
        default_factory=lambda: [InstitutionalRole.GUEST]
    )
    role_mapping: Dict[str, List[InstitutionalRole]] = field(default_factory=dict)
    api_key_expiry: int = 31536000  # 1 year in seconds
    max_upload_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    allowed_file_types: List[str] = field(default_factory=lambda: ["*"])

    @classmethod
    def get_default_policies(cls) -> Dict[str, "InstitutionalPolicy"]:
        """Get default policies for example institutions."""
        return {
            "example_research": cls(
                institution="example_research",
                require_2fa=True,
                allowed_domains=["example-research.org"],
                session_timeout=7200,  # 2 hours
                require_institutional_email=True,
                default_roles=[InstitutionalRole.RESEARCHER],
                role_mapping={
                    "researcher": [InstitutionalRole.RESEARCHER],
                    "professor": [
                        InstitutionalRole.PROFESSOR,
                        InstitutionalRole.RESEARCHER,
                    ],
                    "librarian": [InstitutionalRole.LIBRARIAN],
                    "admin": [InstitutionalRole.ADMIN],
                    "student": [InstitutionalRole.STUDENT],
                },
                max_upload_size=50
                * 1024
                * 1024
                * 1024,  # 50GB for research institution
                allowed_file_types=[
                    "pdf",
                    "doc",
                    "docx",
                    "txt",
                    "jpg",
                    "png",
                    "tiff",
                    "xml",
                    "csv",
                ],
            ),
            "example_library": cls(
                institution="example_library",
                require_2fa=True,
                allowed_domains=["example-library.org"],
                session_timeout=1800,  # 30 minutes for security
                require_institutional_email=True,
                default_roles=[InstitutionalRole.LIBRARIAN],
                role_mapping={
                    "librarian": [InstitutionalRole.LIBRARIAN],
                    "archivist": [
                        InstitutionalRole.ARCHIVIST,
                        InstitutionalRole.LIBRARIAN,
                    ],
                    "curator": [InstitutionalRole.CURATOR],
                    "admin": [InstitutionalRole.ADMIN],
                    "researcher": [InstitutionalRole.RESEARCHER],
                },
                max_upload_size=100 * 1024 * 1024 * 1024,  # 100GB for national library
                allowed_file_types=["*"],  # All file types allowed
            ),
            "example_university": cls(
                institution="example_university",
                require_2fa=False,
                allowed_domains=[
                    "example-university.edu",
                    "student.example-university.edu",
                ],
                session_timeout=3600,
                require_institutional_email=True,
                default_roles=[InstitutionalRole.STUDENT],
                role_mapping={
                    "student": [InstitutionalRole.STUDENT],
                    "researcher": [InstitutionalRole.RESEARCHER],
                    "professor": [
                        InstitutionalRole.PROFESSOR,
                        InstitutionalRole.RESEARCHER,
                    ],
                    "staff": [InstitutionalRole.TECH_SUPPORT],
                    "admin": [InstitutionalRole.ADMIN],
                },
                max_upload_size=20 * 1024 * 1024 * 1024,  # 20GB for university
                allowed_file_types=[
                    "pdf",
                    "doc",
                    "docx",
                    "txt",
                    "jpg",
                    "png",
                    "csv",
                    "xlsx",
                    "ppt",
                    "pptx",
                ],
            ),
            "consortium_member": cls(
                institution="consortium_member",
                require_2fa=False,
                allowed_domains=["*"],  # Multiple institutions
                session_timeout=7200,
                require_institutional_email=False,
                auto_provision_users=True,
                default_roles=[InstitutionalRole.RESEARCHER],
                role_mapping={
                    "researcher": [InstitutionalRole.RESEARCHER],
                    "professor": [
                        InstitutionalRole.PROFESSOR,
                        InstitutionalRole.RESEARCHER,
                    ],
                    "librarian": [InstitutionalRole.LIBRARIAN],
                    "student": [InstitutionalRole.STUDENT],
                    "admin": [InstitutionalRole.ADMIN],
                },
                max_upload_size=200
                * 1024
                * 1024
                * 1024,  # 200GB for research consortium
                allowed_file_types=["*"],
            ),
        }


class InstitutionalAuthManager:
    """Manages institutional authentication and user provisioning."""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser(
            "~/.nakala/institutional_auth.json"
        )
        self.providers: Dict[str, SSOProvider] = {}
        self.policies: Dict[str, InstitutionalPolicy] = {}
        self.user_store_path = os.path.expanduser("~/.nakala/users.json")
        self.session_store_path = os.path.expanduser("~/.nakala/sessions.json")

        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        # Load configuration
        self._load_configuration()
        self._initialize_providers()

    def _load_configuration(self):
        """Load institutional authentication configuration."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    config = json.load(f)

                # Load institutional policies
                for inst_name, policy_data in config.get("institutions", {}).items():
                    self.policies[inst_name] = InstitutionalPolicy(**policy_data)
            else:
                # Use default policies
                self.policies = InstitutionalPolicy.get_default_policies()
                self._save_configuration()

        except Exception as e:
            logger.error(f"Failed to load institutional auth config: {e}")
            self.policies = InstitutionalPolicy.get_default_policies()

    def _save_configuration(self):
        """Save institutional authentication configuration."""
        try:
            config = {
                "institutions": {
                    name: {
                        "institution": policy.institution,
                        "require_2fa": policy.require_2fa,
                        "allowed_domains": policy.allowed_domains,
                        "session_timeout": policy.session_timeout,
                        "max_concurrent_sessions": policy.max_concurrent_sessions,
                        "require_institutional_email": policy.require_institutional_email,
                        "auto_provision_users": policy.auto_provision_users,
                        "default_roles": [role.value for role in policy.default_roles],
                        "role_mapping": {
                            k: [role.value for role in v]
                            for k, v in policy.role_mapping.items()
                        },
                        "api_key_expiry": policy.api_key_expiry,
                        "max_upload_size": policy.max_upload_size,
                        "allowed_file_types": policy.allowed_file_types,
                    }
                    for name, policy in self.policies.items()
                }
            }

            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save institutional auth config: {e}")

    def _initialize_providers(self):
        """Initialize SSO providers for all configured institutions."""
        for institution in self.policies.keys():
            try:
                provider = InstitutionalSSOFactory.create_provider(institution)
                self.providers[institution] = provider
                logger.info(f"Initialized SSO provider for {institution}")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize SSO provider for {institution}: {e}"
                )

    def authenticate_user(
        self, institution: str, callback_data: Dict[str, Any]
    ) -> AuthenticationResult:
        """Authenticate user through institutional SSO."""
        if institution not in self.providers:
            return AuthenticationResult(
                success=False,
                user_id="",
                email="",
                name="",
                institution="",
                roles=[],
                attributes={},
                error_message=f"No SSO provider configured for {institution}",
            )

        # Authenticate through SSO provider
        auth_result = self.providers[institution].handle_callback(callback_data)

        if not auth_result.success:
            return auth_result

        # Apply institutional policies
        policy = self.policies.get(institution)
        if policy:
            # Validate email domain if required
            if policy.require_institutional_email and policy.allowed_domains:
                email_domain = (
                    auth_result.email.split("@")[-1] if "@" in auth_result.email else ""
                )
                if (
                    policy.allowed_domains != ["*"]
                    and email_domain not in policy.allowed_domains
                ):
                    return AuthenticationResult(
                        success=False,
                        user_id="",
                        email="",
                        name="",
                        institution="",
                        roles=[],
                        attributes={},
                        error_message=f"Email domain {email_domain} not allowed for {institution}",
                    )

        # Create or update user profile
        user_profile = self._create_or_update_user(auth_result, institution)

        # Generate session and API key if needed
        if not user_profile.api_key:
            user_profile.api_key = self._generate_api_key(user_profile.user_id)

        user_profile.last_login = datetime.now()
        self._save_user_profile(user_profile)

        # Update authentication result with institutional context
        auth_result.attributes["institutional_roles"] = [
            role.value for role in user_profile.institutional_roles
        ]
        auth_result.attributes["api_key"] = user_profile.api_key

        return auth_result

    def _create_or_update_user(
        self, auth_result: AuthenticationResult, institution: str
    ) -> UserProfile:
        """Create or update user profile with institutional roles."""
        policy = self.policies.get(institution)

        # Load existing user or create new
        user_profile = self._load_user_profile(auth_result.user_id)

        if not user_profile:
            # Create new user
            user_profile = UserProfile(
                user_id=auth_result.user_id,
                email=auth_result.email,
                name=auth_result.name,
                institution=institution,
                attributes=auth_result.attributes,
            )

        # Update user information
        user_profile.email = auth_result.email
        user_profile.name = auth_result.name
        user_profile.attributes.update(auth_result.attributes)

        # Map institutional roles
        if policy:
            user_profile.institutional_roles = policy.default_roles.copy()

            # Apply role mapping based on SSO attributes
            for sso_role in auth_result.roles:
                if sso_role in policy.role_mapping:
                    user_profile.institutional_roles.extend(
                        policy.role_mapping[sso_role]
                    )

            # Remove duplicates
            user_profile.institutional_roles = list(
                set(user_profile.institutional_roles)
            )

        return user_profile

    def _load_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load user profile from storage."""
        try:
            if os.path.exists(self.user_store_path):
                with open(self.user_store_path, "r") as f:
                    users_data = json.load(f)

                user_data = users_data.get(user_id)
                if user_data:
                    # Convert role strings back to enums
                    institutional_roles = [
                        InstitutionalRole(role)
                        for role in user_data.get("institutional_roles", [])
                    ]

                    return UserProfile(
                        user_id=user_data["user_id"],
                        email=user_data["email"],
                        name=user_data["name"],
                        institution=user_data["institution"],
                        institutional_roles=institutional_roles,
                        nakala_roles=user_data.get("nakala_roles", []),
                        attributes=user_data.get("attributes", {}),
                        created_at=datetime.fromisoformat(
                            user_data.get("created_at", datetime.now().isoformat())
                        ),
                        last_login=(
                            datetime.fromisoformat(user_data["last_login"])
                            if user_data.get("last_login")
                            else None
                        ),
                        api_key=user_data.get("api_key"),
                        preferences=user_data.get("preferences", {}),
                    )

        except Exception as e:
            logger.error(f"Failed to load user profile for {user_id}: {e}")

        return None

    def _save_user_profile(self, user_profile: UserProfile):
        """Save user profile to storage."""
        try:
            users_data = {}
            if os.path.exists(self.user_store_path):
                with open(self.user_store_path, "r") as f:
                    users_data = json.load(f)

            users_data[user_profile.user_id] = {
                "user_id": user_profile.user_id,
                "email": user_profile.email,
                "name": user_profile.name,
                "institution": user_profile.institution,
                "institutional_roles": [
                    role.value for role in user_profile.institutional_roles
                ],
                "nakala_roles": user_profile.nakala_roles,
                "attributes": user_profile.attributes,
                "created_at": user_profile.created_at.isoformat(),
                "last_login": (
                    user_profile.last_login.isoformat()
                    if user_profile.last_login
                    else None
                ),
                "api_key": user_profile.api_key,
                "preferences": user_profile.preferences,
            }

            with open(self.user_store_path, "w") as f:
                json.dump(users_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save user profile: {e}")

    def _generate_api_key(self, user_id: str) -> str:
        """Generate API key for user."""
        # Create unique API key based on user ID and timestamp
        data = f"{user_id}:{datetime.now().isoformat()}:{os.urandom(16).hex()}"
        return hashlib.sha256(data.encode()).hexdigest()

    def get_user_by_api_key(self, api_key: str) -> Optional[UserProfile]:
        """Get user profile by API key."""
        try:
            if os.path.exists(self.user_store_path):
                with open(self.user_store_path, "r") as f:
                    users_data = json.load(f)

                for user_id, user_data in users_data.items():
                    if user_data.get("api_key") == api_key:
                        return self._load_user_profile(user_id)

        except Exception as e:
            logger.error(f"Failed to lookup user by API key: {e}")

        return None

    def validate_user_permissions(
        self, user_profile: UserProfile, action: str, resource: str = None
    ) -> bool:
        """Validate user permissions for specific actions."""
        # Get institution policy (if needed for future validation)
        self.policies.get(user_profile.institution)

        # Admin users have all permissions
        if user_profile.is_admin:
            return True

        # Define permission mappings
        permission_map = {
            "upload_data": user_profile.can_upload_data,
            "create_collection": user_profile.can_manage_collections,
            "modify_metadata": user_profile.can_manage_collections,
            "delete_data": user_profile.is_admin,  # Only admins can delete
            "manage_users": user_profile.is_admin,
            "view_analytics": user_profile.can_manage_collections,
        }

        return permission_map.get(action, False)

    def get_institution_policy(self, institution: str) -> Optional[InstitutionalPolicy]:
        """Get institutional policy."""
        return self.policies.get(institution)

    def list_supported_institutions(self) -> List[str]:
        """List supported institutions."""
        return list(self.policies.keys())

    def add_institution(
        self,
        institution: str,
        policy: InstitutionalPolicy,
        sso_config: Dict[str, Any] = None,
    ):
        """Add new institutional configuration."""
        self.policies[institution] = policy

        if sso_config:
            try:
                provider = InstitutionalSSOFactory.create_provider(
                    institution, sso_config
                )
                self.providers[institution] = provider
            except Exception as e:
                logger.error(f"Failed to create SSO provider for {institution}: {e}")

        self._save_configuration()

    def get_auth_url(
        self, institution: str, redirect_uri: str, state: str = None
    ) -> Optional[str]:
        """Get authentication URL for institution."""
        provider = self.providers.get(institution)
        if provider:
            return provider.get_auth_url(redirect_uri, state)
        return None
