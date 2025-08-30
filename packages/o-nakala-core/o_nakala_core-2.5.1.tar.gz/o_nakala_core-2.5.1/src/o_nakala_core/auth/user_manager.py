"""
User management system for O-Nakala Core.
Handles user profiles, roles, and institutional relationships.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .institutional_auth import UserProfile, InstitutionalRole

logger = logging.getLogger(__name__)


class UserStatus(Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    ARCHIVED = "archived"


@dataclass
class UserActivity:
    """User activity record."""

    user_id: str
    timestamp: datetime
    action: str
    resource: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    user_agent: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "resource": self.resource,
            "metadata": self.metadata,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserActivity":
        """Create from dictionary."""
        return cls(
            user_id=data["user_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            action=data["action"],
            resource=data.get("resource", ""),
            metadata=data.get("metadata", {}),
            ip_address=data.get("ip_address", ""),
            user_agent=data.get("user_agent", ""),
        )


@dataclass
class UserStats:
    """User statistics and analytics."""

    user_id: str
    total_uploads: int = 0
    total_collections: int = 0
    total_data_size: int = 0  # bytes
    last_activity: Optional[datetime] = None
    preferred_language: str = "fr"
    most_used_metadata_fields: List[str] = field(default_factory=list)
    collaborators: List[str] = field(default_factory=list)
    favorite_keywords: List[str] = field(default_factory=list)
    quality_score: float = 0.0  # 0-1 score based on metadata completeness

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "total_uploads": self.total_uploads,
            "total_collections": self.total_collections,
            "total_data_size": self.total_data_size,
            "last_activity": (
                self.last_activity.isoformat() if self.last_activity else None
            ),
            "preferred_language": self.preferred_language,
            "most_used_metadata_fields": self.most_used_metadata_fields,
            "collaborators": self.collaborators,
            "favorite_keywords": self.favorite_keywords,
            "quality_score": self.quality_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserStats":
        """Create from dictionary."""
        return cls(
            user_id=data["user_id"],
            total_uploads=data.get("total_uploads", 0),
            total_collections=data.get("total_collections", 0),
            total_data_size=data.get("total_data_size", 0),
            last_activity=(
                datetime.fromisoformat(data["last_activity"])
                if data.get("last_activity")
                else None
            ),
            preferred_language=data.get("preferred_language", "fr"),
            most_used_metadata_fields=data.get("most_used_metadata_fields", []),
            collaborators=data.get("collaborators", []),
            favorite_keywords=data.get("favorite_keywords", []),
            quality_score=data.get("quality_score", 0.0),
        )


class UserManager:
    """Comprehensive user management system."""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/.nakala")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.activity_file = os.path.join(self.data_dir, "user_activity.json")
        self.stats_file = os.path.join(self.data_dir, "user_stats.json")

        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

    def create_user(
        self,
        user_id: str,
        email: str,
        name: str,
        institution: str,
        initial_roles: List[InstitutionalRole] = None,
    ) -> UserProfile:
        """Create new user profile."""

        # Check if user already exists
        existing_user = self.get_user(user_id)
        if existing_user:
            raise ValueError(f"User {user_id} already exists")

        # Create user profile
        user_profile = UserProfile(
            user_id=user_id,
            email=email,
            name=name,
            institution=institution,
            institutional_roles=initial_roles or [InstitutionalRole.GUEST],
            created_at=datetime.now(),
        )

        # Generate API key
        user_profile.api_key = self._generate_api_key(user_id)

        # Save user
        self._save_user(user_profile)

        # Initialize user stats
        user_stats = UserStats(user_id=user_id)
        self._save_user_stats(user_stats)

        # Log activity
        self.log_activity(
            user_id=user_id,
            action="user_created",
            metadata={
                "institution": institution,
                "roles": [role.value for role in user_profile.institutional_roles],
            },
        )

        logger.info(f"Created user {user_id} for institution {institution}")
        return user_profile

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID."""
        users = self._load_users()
        user_data = users.get(user_id)

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

        return None

    def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user profile by email."""
        users = self._load_users()

        for user_data in users.values():
            if user_data.get("email") == email:
                return self.get_user(user_data["user_id"])

        return None

    def get_user_by_api_key(self, api_key: str) -> Optional[UserProfile]:
        """Get user profile by API key."""
        users = self._load_users()

        for user_data in users.values():
            if user_data.get("api_key") == api_key:
                return self.get_user(user_data["user_id"])

        return None

    def update_user(self, user_profile: UserProfile) -> bool:
        """Update user profile."""
        try:
            self._save_user(user_profile)

            self.log_activity(
                user_id=user_profile.user_id,
                action="user_updated",
                metadata={"updated_fields": ["profile"]},
            )

            return True
        except Exception as e:
            logger.error(f"Failed to update user {user_profile.user_id}: {e}")
            return False

    def update_user_roles(self, user_id: str, roles: List[InstitutionalRole]) -> bool:
        """Update user's institutional roles."""
        user_profile = self.get_user(user_id)
        if not user_profile:
            return False

        old_roles = user_profile.institutional_roles.copy()
        user_profile.institutional_roles = roles

        if self.update_user(user_profile):
            self.log_activity(
                user_id=user_id,
                action="roles_updated",
                metadata={
                    "old_roles": [role.value for role in old_roles],
                    "new_roles": [role.value for role in roles],
                },
            )
            return True

        return False

    def update_user_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> bool:
        """Update user preferences."""
        user_profile = self.get_user(user_id)
        if not user_profile:
            return False

        user_profile.preferences.update(preferences)

        if self.update_user(user_profile):
            self.log_activity(
                user_id=user_id,
                action="preferences_updated",
                metadata={"updated_preferences": list(preferences.keys())},
            )
            return True

        return False

    def deactivate_user(self, user_id: str, reason: str = "") -> bool:
        """Deactivate user account."""
        user_profile = self.get_user(user_id)
        if not user_profile:
            return False

        user_profile.attributes["status"] = UserStatus.INACTIVE.value
        user_profile.attributes["deactivated_at"] = datetime.now().isoformat()
        user_profile.attributes["deactivation_reason"] = reason

        if self.update_user(user_profile):
            self.log_activity(
                user_id=user_id, action="user_deactivated", metadata={"reason": reason}
            )
            return True

        return False

    def reactivate_user(self, user_id: str) -> bool:
        """Reactivate user account."""
        user_profile = self.get_user(user_id)
        if not user_profile:
            return False

        user_profile.attributes["status"] = UserStatus.ACTIVE.value
        user_profile.attributes.pop("deactivated_at", None)
        user_profile.attributes.pop("deactivation_reason", None)

        if self.update_user(user_profile):
            self.log_activity(user_id=user_id, action="user_reactivated")
            return True

        return False

    def list_users(
        self,
        institution: str = None,
        role: InstitutionalRole = None,
        status: UserStatus = None,
    ) -> List[UserProfile]:
        """List users with optional filtering."""
        users = self._load_users()
        user_profiles = []

        for user_data in users.values():
            # Apply filters
            if institution and user_data.get("institution") != institution:
                continue

            if role:
                user_roles = [
                    InstitutionalRole(r)
                    for r in user_data.get("institutional_roles", [])
                ]
                if role not in user_roles:
                    continue

            if status:
                user_status = user_data.get("attributes", {}).get("status")
                if user_status != status.value:
                    continue

            user_profile = self.get_user(user_data["user_id"])
            if user_profile:
                user_profiles.append(user_profile)

        return user_profiles

    def get_institution_users(self, institution: str) -> List[UserProfile]:
        """Get all users for an institution."""
        return self.list_users(institution=institution)

    def get_user_collaborators(self, user_id: str) -> List[UserProfile]:
        """Get users who frequently collaborate with this user."""
        user_stats = self.get_user_stats(user_id)
        if not user_stats:
            return []

        collaborators = []
        for collaborator_id in user_stats.collaborators:
            collaborator = self.get_user(collaborator_id)
            if collaborator:
                collaborators.append(collaborator)

        return collaborators

    def log_activity(
        self,
        user_id: str,
        action: str,
        resource: str = "",
        metadata: Dict[str, Any] = None,
        ip_address: str = "",
        user_agent: str = "",
    ):
        """Log user activity."""
        activity = UserActivity(
            user_id=user_id,
            timestamp=datetime.now(),
            action=action,
            resource=resource,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Load existing activities
        activities = self._load_activities()

        # Add new activity
        activities.append(activity.to_dict())

        # Keep only last 1000 activities per user to prevent file size issues
        user_activities = [a for a in activities if a["user_id"] == user_id]
        if len(user_activities) > 1000:
            # Remove oldest activities for this user
            activities = [a for a in activities if a["user_id"] != user_id]
            activities.extend(user_activities[-1000:])

        # Save activities
        self._save_activities(activities)

        # Update user stats
        self._update_user_stats_from_activity(activity)

    def get_user_activity(
        self,
        user_id: str,
        limit: int = 100,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> List[UserActivity]:
        """Get user activity history."""
        activities = self._load_activities()
        user_activities = []

        for activity_data in activities:
            if activity_data["user_id"] != user_id:
                continue

            activity = UserActivity.from_dict(activity_data)

            # Apply date filters
            if start_date and activity.timestamp < start_date:
                continue
            if end_date and activity.timestamp > end_date:
                continue

            user_activities.append(activity)

        # Sort by timestamp (newest first) and limit
        user_activities.sort(key=lambda a: a.timestamp, reverse=True)
        return user_activities[:limit]

    def get_user_stats(self, user_id: str) -> Optional[UserStats]:
        """Get user statistics."""
        stats_data = self._load_user_stats()
        user_stats_data = stats_data.get(user_id)

        if user_stats_data:
            return UserStats.from_dict(user_stats_data)

        return None

    def update_user_stats(self, user_stats: UserStats) -> bool:
        """Update user statistics."""
        try:
            self._save_user_stats(user_stats)
            return True
        except Exception as e:
            logger.error(f"Failed to update user stats for {user_stats.user_id}: {e}")
            return False

    def _generate_api_key(self, user_id: str) -> str:
        """Generate unique API key for user."""
        data = f"{user_id}:{datetime.now().isoformat()}:{os.urandom(16).hex()}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _save_user(self, user_profile: UserProfile):
        """Save user profile to storage."""
        users = self._load_users()

        users[user_profile.user_id] = {
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
                user_profile.last_login.isoformat() if user_profile.last_login else None
            ),
            "api_key": user_profile.api_key,
            "preferences": user_profile.preferences,
        }

        with open(self.users_file, "w") as f:
            json.dump(users, f, indent=2)

    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load users from storage."""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load users: {e}")

        return {}

    def _save_activities(self, activities: List[Dict[str, Any]]):
        """Save activities to storage."""
        try:
            with open(self.activity_file, "w") as f:
                json.dump(activities, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save activities: {e}")

    def _load_activities(self) -> List[Dict[str, Any]]:
        """Load activities from storage."""
        try:
            if os.path.exists(self.activity_file):
                with open(self.activity_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load activities: {e}")

        return []

    def _save_user_stats(self, user_stats: UserStats):
        """Save user statistics."""
        stats_data = self._load_user_stats()
        stats_data[user_stats.user_id] = user_stats.to_dict()

        try:
            with open(self.stats_file, "w") as f:
                json.dump(stats_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user stats: {e}")

    def _load_user_stats(self) -> Dict[str, Dict[str, Any]]:
        """Load user statistics."""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load user stats: {e}")

        return {}

    def _update_user_stats_from_activity(self, activity: UserActivity):
        """Update user statistics based on activity."""
        user_stats = self.get_user_stats(activity.user_id)

        if not user_stats:
            user_stats = UserStats(user_id=activity.user_id)

        # Update last activity
        user_stats.last_activity = activity.timestamp

        # Update counts based on activity type
        if activity.action == "data_uploaded":
            user_stats.total_uploads += 1
            if "file_size" in activity.metadata:
                user_stats.total_data_size += activity.metadata["file_size"]

        elif activity.action == "collection_created":
            user_stats.total_collections += 1

        elif activity.action == "metadata_updated":
            if "fields" in activity.metadata:
                for metadata_field in activity.metadata["fields"]:
                    if metadata_field not in user_stats.most_used_metadata_fields:
                        user_stats.most_used_metadata_fields.append(metadata_field)

        # Save updated stats
        self.update_user_stats(user_stats)
