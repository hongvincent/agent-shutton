# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Session management for pause/resume functionality."""

import json
import os
import pickle
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ResearchSession:
    """Research session state for pause/resume."""

    session_id: str
    query: str
    status: str  # 'running', 'paused', 'completed', 'failed'
    stage: str  # Current processing stage
    created_at: str
    updated_at: str

    # Progress tracking
    papers_found: int = 0
    papers_analyzed: int = 0
    current_paper_index: int = 0

    # State data
    search_results: Optional[Dict] = None
    analyzed_papers: list = None
    drug_interactions: Optional[Dict] = None
    synthesis_results: Optional[Dict] = None
    report: Optional[str] = None

    # Configuration
    config: Optional[Dict] = None

    def __post_init__(self):
        """Initialize lists if None."""
        if self.analyzed_papers is None:
            self.analyzed_papers = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ResearchSession":
        """Create session from dictionary."""
        return cls(**data)


class SessionManager:
    """
    Manages research sessions with pause/resume capability.

    Implements checkpoint-based session persistence, allowing
    long-running research tasks to be paused and resumed.
    """

    def __init__(self, storage_dir: str = "./research_sessions"):
        """
        Initialize Session Manager.

        Args:
            storage_dir: Directory for session storage
        """
        self.storage_dir = storage_dir
        self.sessions: Dict[str, ResearchSession] = {}
        self._ensure_storage_dir()
        self._load_sessions()

    def _ensure_storage_dir(self):
        """Ensure storage directory exists."""
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_session_path(self, session_id: str) -> str:
        """Get file path for a session."""
        return os.path.join(self.storage_dir, f"{session_id}.json")

    def _get_checkpoint_path(self, session_id: str) -> str:
        """Get file path for session checkpoint (binary data)."""
        return os.path.join(self.storage_dir, f"{session_id}.checkpoint")

    def _load_sessions(self):
        """Load existing sessions from disk."""
        if not os.path.exists(self.storage_dir):
            return

        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                session_id = filename[:-5]  # Remove .json
                try:
                    session = self.load_session(session_id)
                    if session:
                        self.sessions[session_id] = session
                except Exception as e:
                    print(f"Error loading session {session_id}: {e}")

    def create_session(
        self,
        session_id: str,
        query: str,
        config: Optional[Dict] = None
    ) -> ResearchSession:
        """
        Create a new research session.

        Args:
            session_id: Unique session identifier
            query: Research query
            config: Session configuration

        Returns:
            Created ResearchSession
        """
        now = datetime.now().isoformat()

        session = ResearchSession(
            session_id=session_id,
            query=query,
            status="running",
            stage="initializing",
            created_at=now,
            updated_at=now,
            config=config or {}
        )

        self.sessions[session_id] = session
        self.save_session(session)

        return session

    def get_session(self, session_id: str) -> Optional[ResearchSession]:
        """
        Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            ResearchSession if found, None otherwise
        """
        return self.sessions.get(session_id)

    def save_session(self, session: ResearchSession):
        """
        Save session to disk.

        Args:
            session: ResearchSession to save
        """
        session.updated_at = datetime.now().isoformat()

        # Save session metadata as JSON
        filepath = self._get_session_path(session.session_id)
        with open(filepath, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)

        # Update in-memory cache
        self.sessions[session.session_id] = session

    def load_session(self, session_id: str) -> Optional[ResearchSession]:
        """
        Load session from disk.

        Args:
            session_id: Session identifier

        Returns:
            ResearchSession if found, None otherwise
        """
        filepath = self._get_session_path(session_id)

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return ResearchSession.from_dict(data)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def pause_session(self, session_id: str) -> bool:
        """
        Pause a running session.

        Args:
            session_id: Session to pause

        Returns:
            True if paused successfully, False otherwise
        """
        session = self.get_session(session_id)

        if not session or session.status != "running":
            return False

        session.status = "paused"
        session.updated_at = datetime.now().isoformat()
        self.save_session(session)

        return True

    def resume_session(self, session_id: str) -> Optional[ResearchSession]:
        """
        Resume a paused session.

        Args:
            session_id: Session to resume

        Returns:
            ResearchSession if resumed, None if failed
        """
        session = self.get_session(session_id)

        if not session or session.status != "paused":
            return None

        session.status = "running"
        session.updated_at = datetime.now().isoformat()
        self.save_session(session)

        return session

    def complete_session(self, session_id: str):
        """
        Mark session as completed.

        Args:
            session_id: Session to complete
        """
        session = self.get_session(session_id)

        if session:
            session.status = "completed"
            session.stage = "completed"
            self.save_session(session)

    def fail_session(self, session_id: str, error: str):
        """
        Mark session as failed.

        Args:
            session_id: Session that failed
            error: Error message
        """
        session = self.get_session(session_id)

        if session:
            session.status = "failed"
            session.stage = f"failed: {error}"
            self.save_session(session)

    def update_progress(
        self,
        session_id: str,
        stage: Optional[str] = None,
        papers_found: Optional[int] = None,
        papers_analyzed: Optional[int] = None,
        current_paper_index: Optional[int] = None
    ):
        """
        Update session progress.

        Args:
            session_id: Session to update
            stage: Current processing stage
            papers_found: Number of papers found
            papers_analyzed: Number of papers analyzed
            current_paper_index: Current paper being processed
        """
        session = self.get_session(session_id)

        if not session:
            return

        if stage is not None:
            session.stage = stage
        if papers_found is not None:
            session.papers_found = papers_found
        if papers_analyzed is not None:
            session.papers_analyzed = papers_analyzed
        if current_paper_index is not None:
            session.current_paper_index = current_paper_index

        self.save_session(session)

    def save_checkpoint(self, session_id: str, checkpoint_data: Any):
        """
        Save a checkpoint with arbitrary data (for complex state).

        Args:
            session_id: Session identifier
            checkpoint_data: Any Python object to checkpoint
        """
        checkpoint_path = self._get_checkpoint_path(session_id)

        with open(checkpoint_path, 'wb') as f:
            pickle.dump(checkpoint_data, f)

    def load_checkpoint(self, session_id: str) -> Optional[Any]:
        """
        Load checkpoint data.

        Args:
            session_id: Session identifier

        Returns:
            Checkpoint data if exists, None otherwise
        """
        checkpoint_path = self._get_checkpoint_path(session_id)

        if not os.path.exists(checkpoint_path):
            return None

        try:
            with open(checkpoint_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading checkpoint for {session_id}: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and its data.

        Args:
            session_id: Session to delete

        Returns:
            True if deleted, False if not found
        """
        if session_id not in self.sessions:
            return False

        # Delete from memory
        del self.sessions[session_id]

        # Delete files
        session_path = self._get_session_path(session_id)
        checkpoint_path = self._get_checkpoint_path(session_id)

        if os.path.exists(session_path):
            os.remove(session_path)
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)

        return True

    def list_sessions(
        self,
        status: Optional[str] = None
    ) -> list[ResearchSession]:
        """
        List all sessions, optionally filtered by status.

        Args:
            status: Filter by status ('running', 'paused', 'completed', 'failed')

        Returns:
            List of ResearchSession objects
        """
        sessions = list(self.sessions.values())

        if status:
            sessions = [s for s in sessions if s.status == status]

        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda s: s.updated_at, reverse=True)

        return sessions

    def get_statistics(self) -> Dict:
        """
        Get statistics about sessions.

        Returns:
            Dictionary with statistics
        """
        by_status = {}
        total_papers = 0

        for session in self.sessions.values():
            by_status[session.status] = by_status.get(session.status, 0) + 1
            total_papers += session.papers_analyzed

        return {
            "total_sessions": len(self.sessions),
            "by_status": by_status,
            "total_papers_analyzed": total_papers
        }
