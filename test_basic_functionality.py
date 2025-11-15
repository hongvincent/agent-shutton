#!/usr/bin/env python3
"""Test basic functionality of MedResearch AI components."""

import asyncio
import tempfile
import shutil
from datetime import datetime

print("=" * 80)
print("Testing MedResearch AI Basic Functionality")
print("=" * 80)

# Test 1: Memory Bank
print("\n[Test 1] Testing Memory Bank...")
try:
    from medresearch_agent.utils import ResearchMemoryBank, ResearchMemory

    with tempfile.TemporaryDirectory() as tmpdir:
        memory_bank = ResearchMemoryBank(storage_dir=tmpdir)

        # Store memory
        memory = ResearchMemory(
            memory_id="test_001",
            query="diabetes treatment",
            timestamp=datetime.now().isoformat(),
            papers_analyzed=10,
            key_findings=["Finding 1", "Finding 2"],
            evidence_quality=8.5
        )
        memory_bank.store_memory(memory)

        # Retrieve memory
        retrieved = memory_bank.retrieve_memory("test_001")
        assert retrieved is not None
        assert retrieved.query == "diabetes treatment"

        print("✅ Memory Bank: PASSED")
except Exception as e:
    print(f"❌ Memory Bank: FAILED - {e}")

# Test 2: SessionManager
print("\n[Test 2] Testing SessionManager...")
try:
    from medresearch_agent.utils import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(storage_dir=tmpdir)

        # Create session
        session = manager.create_session(
            session_id="test_session",
            query="test query",
            config={"max_papers": 50}
        )
        assert session.session_id == "test_session"
        assert session.status == "running"

        # Pause session
        success = manager.pause_session("test_session")
        assert success is True

        paused = manager.get_session("test_session")
        assert paused.status == "paused"

        # Resume session
        resumed = manager.resume_session("test_session")
        assert resumed is not None
        assert resumed.status == "running"

        print("✅ SessionManager: PASSED")
except Exception as e:
    print(f"❌ SessionManager: FAILED - {e}")

# Test 3: A2A Protocol
print("\n[Test 3] Testing A2A Protocol...")
async def test_a2a():
    try:
        from medresearch_agent.utils import ResearchCoordinationProtocol

        protocol = ResearchCoordinationProtocol()

        # Send research request
        msg_id = await protocol.send_research_request(
            from_agent="test_coordinator",
            to_agent="test_searcher",
            query="test query"
        )
        assert msg_id is not None

        # Receive message
        message = await protocol.receive_message(timeout=1)
        assert message is not None
        assert message.sender == "test_coordinator"

        print("✅ A2A Protocol: PASSED")
    except Exception as e:
        print(f"❌ A2A Protocol: FAILED - {e}")

asyncio.run(test_a2a())

# Test 4: Medical Tools
print("\n[Test 4] Testing Medical Tools...")
try:
    from medresearch_agent.tools.medical_tools import validate_medical_terminology

    result = validate_medical_terminology("Patient diagnosed with diabetes mellitus")
    assert "medical_terms_found" in result
    assert result["medical_terms_found"] > 0

    print("✅ Medical Tools: PASSED")
except Exception as e:
    print(f"❌ Medical Tools: FAILED - {e}")

# Test 5: Observability
print("\n[Test 5] Testing Observability...")
try:
    from medresearch_agent.observability import get_logger, get_metrics_tracker

    logger = get_logger()
    assert logger is not None

    metrics = get_metrics_tracker()
    assert metrics is not None

    # Track a session
    session_metrics = metrics.start_session("test_session")
    assert session_metrics.session_id == "test_session"

    print("✅ Observability: PASSED")
except Exception as e:
    print(f"❌ Observability: FAILED - {e}")

# Test 6: Evaluation
print("\n[Test 6] Testing Evaluation Framework...")
try:
    from medresearch_agent.evaluation import CitationValidator, EvaluationMetrics

    validator = CitationValidator()
    assert validator is not None

    metrics = EvaluationMetrics(
        session_id="test",
        timestamp=datetime.now().isoformat(),
        citation_accuracy_rate=0.95
    )
    assert metrics.session_id == "test"

    print("✅ Evaluation: PASSED")
except Exception as e:
    print(f"❌ Evaluation: FAILED - {e}")

print("\n" + "=" * 80)
print("Basic Functionality Testing Complete")
print("=" * 80)
