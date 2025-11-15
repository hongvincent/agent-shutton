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

"""Tests for advanced features: Memory Bank, A2A Protocol, Sessions, Evaluation."""

import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime

from medresearch_agent.utils.memory_bank import ResearchMemoryBank, ResearchMemory
from medresearch_agent.utils.session_manager import SessionManager, ResearchSession
from medresearch_agent.utils.a2a_protocol import (
    ResearchCoordinationProtocol,
    A2AMessage,
    MessageType,
    MessagePriority
)
from medresearch_agent.evaluation.validators import (
    CitationValidator,
    MedicalAccuracyEvaluator,
    EvidenceQualityValidator,
    CompletenessValidator
)
from medresearch_agent.evaluation.metrics import EvaluationMetrics, generate_evaluation_report


class TestMemoryBank:
    """Test Memory Bank functionality."""

    def test_create_memory_bank(self):
        """Test creating a memory bank."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_bank = ResearchMemoryBank(storage_dir=tmpdir)
            assert memory_bank is not None
            assert len(memory_bank.memories) == 0

    def test_store_and_retrieve_memory(self):
        """Test storing and retrieving memories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_bank = ResearchMemoryBank(storage_dir=tmpdir)

            memory = ResearchMemory(
                memory_id="test_001",
                query="diabetes treatments",
                timestamp=datetime.now().isoformat(),
                papers_analyzed=25,
                key_findings=["Finding 1", "Finding 2"],
                evidence_quality=8.5
            )

            memory_bank.store_memory(memory)

            retrieved = memory_bank.retrieve_memory("test_001")
            assert retrieved is not None
            assert retrieved.query == "diabetes treatments"
            assert retrieved.papers_analyzed == 25

    def test_search_memories(self):
        """Test searching memories by query."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_bank = ResearchMemoryBank(storage_dir=tmpdir)

            # Store multiple memories
            memory1 = ResearchMemory(
                memory_id="mem_001",
                query="diabetes type 2 treatment",
                timestamp=datetime.now().isoformat(),
                papers_analyzed=20,
                key_findings=["Metformin effective"],
                evidence_quality=8.0
            )

            memory2 = ResearchMemory(
                memory_id="mem_002",
                query="hypertension medication",
                timestamp=datetime.now().isoformat(),
                papers_analyzed=15,
                key_findings=["ACE inhibitors"],
                evidence_quality=7.5
            )

            memory_bank.store_memory(memory1)
            memory_bank.store_memory(memory2)

            # Search for diabetes
            results = memory_bank.search_memories("diabetes")
            assert len(results) > 0
            assert any(m.query == "diabetes type 2 treatment" for m in results)

    def test_memory_persistence(self):
        """Test that memories persist across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first instance and store memory
            bank1 = ResearchMemoryBank(storage_dir=tmpdir)
            memory = ResearchMemory(
                memory_id="persist_001",
                query="test persistence",
                timestamp=datetime.now().isoformat(),
                papers_analyzed=10,
                key_findings=["Test finding"],
                evidence_quality=7.0
            )
            bank1.store_memory(memory)

            # Create new instance and verify memory loaded
            bank2 = ResearchMemoryBank(storage_dir=tmpdir)
            assert "persist_001" in bank2.memories
            assert bank2.memories["persist_001"].query == "test persistence"


class TestSessionManager:
    """Test Session Manager functionality."""

    def test_create_session(self):
        """Test creating a research session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(storage_dir=tmpdir)

            session = manager.create_session(
                session_id="sess_001",
                query="diabetes research",
                config={"max_papers": 50}
            )

            assert session is not None
            assert session.session_id == "sess_001"
            assert session.query == "diabetes research"
            assert session.status == "running"

    def test_pause_resume_session(self):
        """Test pausing and resuming sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(storage_dir=tmpdir)

            # Create session
            session = manager.create_session("sess_002", "test query")
            assert session.status == "running"

            # Pause
            success = manager.pause_session("sess_002")
            assert success is True

            paused = manager.get_session("sess_002")
            assert paused.status == "paused"

            # Resume
            resumed = manager.resume_session("sess_002")
            assert resumed is not None
            assert resumed.status == "running"

    def test_update_progress(self):
        """Test updating session progress."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(storage_dir=tmpdir)

            session = manager.create_session("sess_003", "test")

            manager.update_progress(
                "sess_003",
                stage="analyzing",
                papers_found=50,
                papers_analyzed=10
            )

            updated = manager.get_session("sess_003")
            assert updated.stage == "analyzing"
            assert updated.papers_found == 50
            assert updated.papers_analyzed == 10

    def test_session_persistence(self):
        """Test session persistence across manager instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create session with first manager
            manager1 = SessionManager(storage_dir=tmpdir)
            manager1.create_session("sess_004", "persist test")

            # Load with second manager
            manager2 = SessionManager(storage_dir=tmpdir)
            assert "sess_004" in manager2.sessions
            assert manager2.sessions["sess_004"].query == "persist test"


@pytest.mark.asyncio
class TestA2AProtocol:
    """Test Agent-to-Agent Protocol."""

    async def test_send_message(self):
        """Test sending A2A messages."""
        protocol = ResearchCoordinationProtocol()

        message = A2AMessage(
            sender="coordinator",
            receiver="literature_search",
            message_type=MessageType.RESEARCH_REQUEST,
            payload={"query": "diabetes"}
        )

        message_id = await protocol.send_message(message)
        assert message_id is not None
        assert len(protocol.message_log) == 1

    async def test_send_research_request(self):
        """Test sending research request."""
        protocol = ResearchCoordinationProtocol()

        msg_id = await protocol.send_research_request(
            from_agent="coordinator",
            to_agent="pubmed_searcher",
            query="hypertension treatment"
        )

        assert msg_id is not None
        assert protocol.message_queue.qsize() == 1

    async def test_receive_message(self):
        """Test receiving messages."""
        protocol = ResearchCoordinationProtocol()

        # Send a message
        await protocol.send_research_request(
            "agent_a",
            "agent_b",
            "test query"
        )

        # Receive it
        message = await protocol.receive_message(timeout=1)
        assert message is not None
        assert message.sender == "agent_a"
        assert message.receiver == "agent_b"

    async def test_message_statistics(self):
        """Test getting protocol statistics."""
        protocol = ResearchCoordinationProtocol()

        # Send multiple messages
        await protocol.send_research_request("a", "b", "query1")
        await protocol.send_research_results("b", "a", {"results": []})
        await protocol.send_status_update("a", "c", "running", {})

        stats = protocol.get_statistics()
        assert stats["total_messages"] == 3
        assert "by_type" in stats
        assert "by_sender" in stats


class TestEvaluationValidators:
    """Test evaluation validators."""

    def test_citation_validator(self):
        """Test citation validation."""
        validator = CitationValidator()

        # Test AMA format validation
        valid_citation = "Smith AB, Johnson CD. Title here. 2024"
        assert validator.validate_ama_format(valid_citation)

    def test_medical_accuracy_evaluator(self):
        """Test medical accuracy evaluation."""
        evaluator = MedicalAccuracyEvaluator()

        text = "Patient diagnosed with COPD and prescribed bronchodilators for bronchitis symptoms."

        result = evaluator.evaluate_terminology(text)
        assert "medical_terms_found" in result
        assert "terminology_score" in result
        assert result["medical_terms_found"] > 0

    def test_evidence_quality_validator(self):
        """Test evidence quality validation."""
        validator = EvidenceQualityValidator()

        # RCT should have high score
        assert validator.validate_quality_score(9.0, "rct")

        # Case report should not have high score
        assert not validator.validate_quality_score(9.0, "case_report")

    def test_completeness_validator(self):
        """Test report completeness validation."""
        validator = CompletenessValidator()

        sample_report = """
        # Executive Summary
        This is the summary.

        # Background
        Background information.

        # Methodology
        Our methods.

        # Findings
        Key findings here.

        # Evidence
        Evidence synthesis.

        # Implications
        Clinical implications.

        # Limitations
        Study limitations.

        # Recommendations
        Our recommendations.

        # References
        1. Paper citation
        """

        result = validator.validate_report_completeness(sample_report)
        assert result["completeness_score"] >= 0.8
        assert result["complete"] is True


class TestEvaluationMetrics:
    """Test evaluation metrics."""

    def test_metrics_creation(self):
        """Test creating evaluation metrics."""
        metrics = EvaluationMetrics(
            session_id="test_session",
            timestamp=datetime.now().isoformat(),
            total_citations=100,
            valid_citations=95,
            citation_accuracy_rate=0.95,
            total_papers=50,
            high_quality_papers=30,
            average_evidence_score=8.2
        )

        assert metrics.session_id == "test_session"
        assert metrics.citation_accuracy_rate == 0.95

    def test_overall_score_calculation(self):
        """Test overall quality score calculation."""
        metrics = EvaluationMetrics(
            session_id="test",
            timestamp=datetime.now().isoformat(),
            citation_accuracy_rate=0.95,
            average_evidence_score=8.5,
            completeness_score=0.9,
            terminology_score=0.85
        )

        score = metrics.calculate_overall_score()
        assert score > 0
        assert score <= 100

    def test_evaluation_report_generation(self):
        """Test generating evaluation report."""
        metrics = EvaluationMetrics(
            session_id="test_report",
            timestamp=datetime.now().isoformat(),
            total_citations=50,
            valid_citations=48,
            citation_accuracy_rate=0.96,
            total_papers=30,
            high_quality_papers=20,
            average_evidence_score=8.0,
            completeness_score=0.9,
            terminology_score=0.85
        )

        report = generate_evaluation_report(metrics)

        assert "overall_score" in report
        assert "rating" in report
        assert "category_scores" in report
        assert "recommendations" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
