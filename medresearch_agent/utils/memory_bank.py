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

"""Memory Bank implementation for long-term research context storage."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ResearchMemory:
    """Individual research memory entry."""

    memory_id: str
    query: str
    timestamp: str
    papers_analyzed: int
    key_findings: List[str]
    evidence_quality: float
    report_path: Optional[str] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class ResearchMemoryBank:
    """
    Memory Bank for storing and retrieving research history.

    Implements long-term memory for the MedResearch AI system,
    allowing agents to reference past research sessions and build
    on previous findings.
    """

    def __init__(self, storage_dir: str = "./memory_bank"):
        """
        Initialize Memory Bank.

        Args:
            storage_dir: Directory for storing memory files
        """
        self.storage_dir = storage_dir
        self.memories: Dict[str, ResearchMemory] = {}
        self._ensure_storage_dir()
        self._load_memories()

    def _ensure_storage_dir(self):
        """Ensure storage directory exists."""
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_memory_path(self, memory_id: str) -> str:
        """Get file path for a memory."""
        return os.path.join(self.storage_dir, f"{memory_id}.json")

    def _load_memories(self):
        """Load existing memories from disk."""
        if not os.path.exists(self.storage_dir):
            return

        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        memory = ResearchMemory(**data)
                        self.memories[memory.memory_id] = memory
                except Exception as e:
                    print(f"Error loading memory {filename}: {e}")

    def store_memory(self, memory: ResearchMemory):
        """
        Store a research memory.

        Args:
            memory: ResearchMemory to store
        """
        # Add to in-memory cache
        self.memories[memory.memory_id] = memory

        # Persist to disk
        filepath = self._get_memory_path(memory.memory_id)
        with open(filepath, 'w') as f:
            json.dump(memory.to_dict(), f, indent=2)

    def retrieve_memory(self, memory_id: str) -> Optional[ResearchMemory]:
        """
        Retrieve a specific memory.

        Args:
            memory_id: ID of memory to retrieve

        Returns:
            ResearchMemory if found, None otherwise
        """
        return self.memories.get(memory_id)

    def search_memories(self, query: str, limit: int = 10) -> List[ResearchMemory]:
        """
        Search memories by query similarity.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching ResearchMemory objects
        """
        # Simple keyword-based search
        # In production, use embeddings for semantic search
        query_lower = query.lower()
        matches = []

        for memory in self.memories.values():
            # Check if query words appear in memory query or findings
            memory_text = f"{memory.query} {' '.join(memory.key_findings)}".lower()
            if any(word in memory_text for word in query_lower.split()):
                matches.append(memory)

        # Sort by timestamp (most recent first)
        matches.sort(key=lambda m: m.timestamp, reverse=True)

        return matches[:limit]

    def get_recent_memories(self, limit: int = 5) -> List[ResearchMemory]:
        """
        Get most recent memories.

        Args:
            limit: Maximum number of memories to return

        Returns:
            List of recent ResearchMemory objects
        """
        sorted_memories = sorted(
            self.memories.values(),
            key=lambda m: m.timestamp,
            reverse=True
        )
        return sorted_memories[:limit]

    def get_memory_summary(self) -> Dict:
        """
        Get summary of memory bank contents.

        Returns:
            Dictionary with summary statistics
        """
        if not self.memories:
            return {
                "total_memories": 0,
                "total_papers_analyzed": 0,
                "average_quality": 0.0
            }

        total_papers = sum(m.papers_analyzed for m in self.memories.values())
        avg_quality = sum(m.evidence_quality for m in self.memories.values()) / len(self.memories)

        return {
            "total_memories": len(self.memories),
            "total_papers_analyzed": total_papers,
            "average_quality": round(avg_quality, 2),
            "oldest_memory": min(m.timestamp for m in self.memories.values()),
            "newest_memory": max(m.timestamp for m in self.memories.values())
        }

    def clear_old_memories(self, days: int = 90):
        """
        Clear memories older than specified days.

        Args:
            days: Number of days to retain
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        to_delete = []

        for memory_id, memory in self.memories.items():
            memory_time = datetime.fromisoformat(memory.timestamp)
            if memory_time < cutoff:
                to_delete.append(memory_id)

        # Delete from memory and disk
        for memory_id in to_delete:
            del self.memories[memory_id]
            filepath = self._get_memory_path(memory_id)
            if os.path.exists(filepath):
                os.remove(filepath)


def create_memory_bank(storage_dir: str = "./memory_bank") -> ResearchMemoryBank:
    """
    Create and initialize a Memory Bank.

    Args:
        storage_dir: Directory for memory storage

    Returns:
        Initialized ResearchMemoryBank
    """
    return ResearchMemoryBank(storage_dir=storage_dir)
