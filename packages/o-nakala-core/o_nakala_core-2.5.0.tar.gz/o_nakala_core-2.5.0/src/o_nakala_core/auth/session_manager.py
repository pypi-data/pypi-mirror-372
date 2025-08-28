"""
Session management for O-Nakala Core authentication.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import secrets

logger = logging.getLogger(__name__)


@dataclass
class UserSession:
    """User session information."""

    session_id: str
    user_id: str
    institution: str
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime
    ip_address: str = ""
    user_agent: str = ""
    is_active: bool = True
    session_data: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if session is valid and not expired."""
        return (
            self.is_active
            and datetime.now() < self.expires_at
            and self.last_accessed > (datetime.now() - timedelta(hours=24))
        )

    def refresh(self, extend_by: int = 3600):
        """Refresh session expiration."""
        self.last_accessed = datetime.now()
        self.expires_at = datetime.now() + timedelta(seconds=extend_by)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for storage."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "institution": self.institution,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_active": self.is_active,
            "session_data": self.session_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSession":
        """Create session from dictionary."""
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            institution=data["institution"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            ip_address=data.get("ip_address", ""),
            user_agent=data.get("user_agent", ""),
            is_active=data.get("is_active", True),
            session_data=data.get("session_data", {}),
        )


class SessionManager:
    """Manages user sessions for web and CLI interfaces."""

    def __init__(self, session_store_path: str = None):
        self.session_store_path = session_store_path or os.path.expanduser(
            "~/.nakala/sessions.json"
        )
        self.max_sessions_per_user = 5
        self.default_session_timeout = 3600  # 1 hour
        self.max_session_timeout = 86400  # 24 hours

        # Ensure storage directory exists
        os.makedirs(os.path.dirname(self.session_store_path), exist_ok=True)

        # Clean up expired sessions on startup
        self._cleanup_expired_sessions()

    def create_session(
        self,
        user_id: str,
        institution: str,
        timeout: int = None,
        ip_address: str = "",
        user_agent: str = "",
        session_data: Dict[str, Any] = None,
    ) -> UserSession:
        """
        Create new user session.

        Args:
            user_id: User identifier
            institution: Institution identifier
            timeout: Session timeout in seconds
            ip_address: Client IP address
            user_agent: Client user agent
            session_data: Additional session data

        Returns:
            UserSession object
        """
        # Clean up old sessions for this user
        self._cleanup_user_sessions(user_id)

        # Generate secure session ID
        session_id = self._generate_session_id(user_id)

        # Set session timeout
        timeout = timeout or self.default_session_timeout
        timeout = min(timeout, self.max_session_timeout)

        # Create session
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            institution=institution,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=timeout),
            ip_address=ip_address,
            user_agent=user_agent,
            session_data=session_data or {},
        )

        # Save session
        self._save_session(session)

        logger.info(f"Created session {session_id} for user {user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID."""
        sessions = self._load_sessions()
        session_data = sessions.get(session_id)

        if session_data:
            session = UserSession.from_dict(session_data)

            if session.is_valid():
                # Refresh last accessed time
                session.last_accessed = datetime.now()
                self._save_session(session)
                return session
            else:
                # Remove expired session
                self._remove_session(session_id)

        return None

    def get_session_by_token(self, token: str) -> Optional[UserSession]:
        """Get session by token (alias for session ID)."""
        return self.get_session(token)

    def get_user_sessions(self, user_id: str) -> List[UserSession]:
        """Get all active sessions for a user."""
        sessions = self._load_sessions()
        user_sessions = []

        for session_data in sessions.values():
            if session_data["user_id"] == user_id:
                session = UserSession.from_dict(session_data)
                if session.is_valid():
                    user_sessions.append(session)

        return user_sessions

    def refresh_session(
        self, session_id: str, extend_by: int = None
    ) -> Optional[UserSession]:
        """Refresh session expiration."""
        session = self.get_session(session_id)

        if session:
            extend_by = extend_by or self.default_session_timeout
            session.refresh(extend_by)
            self._save_session(session)

        return session

    def terminate_session(self, session_id: str) -> bool:
        """Terminate a specific session."""
        session = self.get_session(session_id)

        if session:
            session.is_active = False
            self._save_session(session)
            logger.info(f"Terminated session {session_id}")
            return True

        return False

    def terminate_user_sessions(self, user_id: str) -> int:
        """Terminate all sessions for a user."""
        sessions = self.get_user_sessions(user_id)
        terminated_count = 0

        for session in sessions:
            if self.terminate_session(session.session_id):
                terminated_count += 1

        return terminated_count

    def update_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data."""
        session = self.get_session(session_id)

        if session:
            session.session_data.update(data)
            self._save_session(session)
            return True

        return False

    def _generate_session_id(self, user_id: str) -> str:
        """Generate secure session ID."""
        timestamp = str(datetime.now().timestamp())
        random_bytes = secrets.token_bytes(16)
        data = f"{user_id}:{timestamp}:{random_bytes.hex()}"

        return hashlib.sha256(data.encode()).hexdigest()

    def _load_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Load sessions from storage."""
        try:
            if os.path.exists(self.session_store_path):
                with open(self.session_store_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")

        return {}

    def _save_sessions(self, sessions: Dict[str, Dict[str, Any]]):
        """Save sessions to storage."""
        try:
            with open(self.session_store_path, "w") as f:
                json.dump(sessions, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")

    def _save_session(self, session: UserSession):
        """Save individual session."""
        sessions = self._load_sessions()
        sessions[session.session_id] = session.to_dict()
        self._save_sessions(sessions)

    def _remove_session(self, session_id: str):
        """Remove session from storage."""
        sessions = self._load_sessions()
        if session_id in sessions:
            del sessions[session_id]
            self._save_sessions(sessions)

    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        sessions = self._load_sessions()
        active_sessions = {}

        for session_id, session_data in sessions.items():
            try:
                session = UserSession.from_dict(session_data)
                if session.is_valid():
                    active_sessions[session_id] = session_data
            except Exception as e:
                logger.warning(f"Invalid session data for {session_id}: {e}")

        if len(active_sessions) != len(sessions):
            self._save_sessions(active_sessions)
            logger.info(
                f"Cleaned up {len(sessions) - len(active_sessions)} expired sessions"
            )

    def _cleanup_user_sessions(self, user_id: str):
        """Clean up old sessions for a user to enforce session limit."""
        user_sessions = self.get_user_sessions(user_id)

        if len(user_sessions) >= self.max_sessions_per_user:
            # Sort by last accessed time and remove oldest
            user_sessions.sort(key=lambda s: s.last_accessed)

            sessions_to_remove = len(user_sessions) - self.max_sessions_per_user + 1
            for i in range(sessions_to_remove):
                self.terminate_session(user_sessions[i].session_id)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        sessions = self._load_sessions()
        active_sessions = []

        for session_data in sessions.values():
            try:
                session = UserSession.from_dict(session_data)
                if session.is_valid():
                    active_sessions.append(session)
            except Exception:
                continue

        # Group by institution
        institution_counts = {}
        for session in active_sessions:
            institution_counts[session.institution] = (
                institution_counts.get(session.institution, 0) + 1
            )

        return {
            "total_sessions": len(sessions),
            "active_sessions": len(active_sessions),
            "expired_sessions": len(sessions) - len(active_sessions),
            "sessions_by_institution": institution_counts,
            "oldest_session": (
                min(active_sessions, key=lambda s: s.created_at).created_at.isoformat()
                if active_sessions
                else None
            ),
            "newest_session": (
                max(active_sessions, key=lambda s: s.created_at).created_at.isoformat()
                if active_sessions
                else None
            ),
        }
