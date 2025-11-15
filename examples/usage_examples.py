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

"""
Usage examples for MedResearch AI advanced features.

This file demonstrates how to use:
- Memory Bank for long-term research context
- A2A Protocol for agent-to-agent communication
- SessionManager for pause/resume functionality
"""

import asyncio
from datetime import datetime

# ✅ Import all advanced features
from medresearch_agent.utils import (
    ResearchMemoryBank,
    ResearchMemory,
    ResearchCoordinationProtocol,
    A2AMessage,
    MessageType,
    MessagePriority,
    SessionManager
)


# =============================================================================
# Example 1: Using Memory Bank
# =============================================================================

def example_memory_bank():
    """
    Demonstrate Memory Bank usage for storing and retrieving research history.

    The Memory Bank allows agents to:
    - Store past research sessions
    - Search previous findings
    - Build on previous work
    - Avoid duplicate research
    """
    print("="*80)
    print("Example 1: Memory Bank Usage")
    print("="*80)

    # Create memory bank
    memory_bank = ResearchMemoryBank(storage_dir="./memory_bank")

    # Store a research memory
    memory = ResearchMemory(
        memory_id="diabetes_research_2025_01",
        query="Latest treatments for Type 2 Diabetes",
        timestamp=datetime.now().isoformat(),
        papers_analyzed=47,
        key_findings=[
            "Metformin remains first-line treatment",
            "GLP-1 agonists show cardiovascular benefits",
            "SGLT2 inhibitors reduce heart failure risk"
        ],
        evidence_quality=8.5,
        report_path="research_reports/diabetes_2025_01.md"
    )

    memory_bank.store_memory(memory)
    print(f"✅ Stored memory: {memory.memory_id}")

    # Retrieve specific memory
    retrieved = memory_bank.retrieve_memory("diabetes_research_2025_01")
    print(f"✅ Retrieved memory: {retrieved.query}")
    print(f"   Papers analyzed: {retrieved.papers_analyzed}")
    print(f"   Evidence quality: {retrieved.evidence_quality}")

    # Search memories by query
    results = memory_bank.search_memories("diabetes")
    print(f"\n✅ Search results for 'diabetes': {len(results)} memories found")

    # Get summary
    summary = memory_bank.get_memory_summary()
    print(f"\n✅ Memory Bank Summary:")
    print(f"   Total memories: {summary['total_memories']}")
    print(f"   Total papers analyzed: {summary['total_papers_analyzed']}")
    print(f"   Average quality: {summary['average_quality']}")

    print("\n" + "="*80 + "\n")


# =============================================================================
# Example 2: Using A2A Protocol
# =============================================================================

async def example_a2a_protocol():
    """
    Demonstrate Agent-to-Agent (A2A) Protocol usage.

    The A2A Protocol enables:
    - Asynchronous communication between agents
    - Request/response patterns
    - Status updates
    - Coordinated research workflows
    """
    print("="*80)
    print("Example 2: A2A Protocol Usage")
    print("="*80)

    # Create A2A protocol
    protocol = ResearchCoordinationProtocol()

    # Example 1: Coordinator sends research request to literature search agent
    print("\n📤 Coordinator → Literature Searcher")
    msg_id = await protocol.send_research_request(
        from_agent="med_research_coordinator",
        to_agent="literature_search_agent",
        query="hypertension treatment guidelines 2025",
        max_results=50,
        databases=["pubmed", "clinicaltrials"]
    )
    print(f"✅ Sent research request, message ID: {msg_id[:8]}...")

    # Example 2: Literature searcher sends results back
    print("\n📥 Literature Searcher → Coordinator")
    await protocol.send_research_results(
        from_agent="literature_search_agent",
        to_agent="med_research_coordinator",
        results={
            "papers_found": 47,
            "papers": [
                {"pmid": "12345678", "title": "Hypertension Guidelines 2025"},
                {"pmid": "87654321", "title": "Novel ACE Inhibitors Study"}
            ]
        },
        correlation_id=msg_id  # Links response to original request
    )
    print("✅ Sent research results back to coordinator")

    # Example 3: Send status update
    print("\n📊 Paper Analyzer → Coordinator (Status Update)")
    await protocol.send_status_update(
        from_agent="paper_analyzer",
        to_agent="med_research_coordinator",
        status="analyzing",
        progress={
            "papers_analyzed": 10,
            "total_papers": 47,
            "current_stage": "methodology_analysis"
        }
    )
    print("✅ Sent status update")

    # Get protocol statistics
    stats = protocol.get_statistics()
    print(f"\n✅ Protocol Statistics:")
    print(f"   Total messages: {stats['total_messages']}")
    print(f"   Messages by type: {stats['by_type']}")
    print(f"   Messages by sender: {stats['by_sender']}")

    print("\n" + "="*80 + "\n")


# =============================================================================
# Example 3: Using SessionManager
# =============================================================================

def example_session_manager():
    """
    Demonstrate SessionManager usage for pause/resume functionality.

    The SessionManager enables:
    - Create research sessions
    - Pause long-running tasks
    - Resume from exact checkpoint
    - Track progress across restarts
    """
    print("="*80)
    print("Example 3: SessionManager Usage")
    print("="*80)

    # Create session manager
    session_manager = SessionManager(storage_dir="./research_sessions")

    # Create a new research session
    print("\n✅ Creating new research session...")
    session = session_manager.create_session(
        session_id="sess_hypertension_2025",
        query="Hypertension treatment guidelines",
        config={"max_papers": 50, "include_trials": True}
    )
    print(f"   Session ID: {session.session_id}")
    print(f"   Query: {session.query}")
    print(f"   Status: {session.status}")

    # Update progress
    print("\n✅ Updating research progress...")
    session_manager.update_progress(
        session.session_id,
        stage="analyzing",
        papers_found=50,
        papers_analyzed=10
    )

    updated = session_manager.get_session(session.session_id)
    print(f"   Stage: {updated.stage}")
    print(f"   Papers found: {updated.papers_found}")
    print(f"   Papers analyzed: {updated.papers_analyzed}")

    # Pause the session
    print("\n⏸️  Pausing session...")
    success = session_manager.pause_session(session.session_id)
    print(f"   Paused: {success}")

    paused = session_manager.get_session(session.session_id)
    print(f"   Status: {paused.status}")

    # Resume the session
    print("\n▶️  Resuming session...")
    resumed = session_manager.resume_session(session.session_id)
    print(f"   Resumed from stage: {resumed.stage}")
    print(f"   Continue from paper: {resumed.current_paper_index}")

    # List all sessions
    print("\n✅ Listing all sessions:")
    all_sessions = session_manager.list_sessions()
    for s in all_sessions:
        print(f"   - {s.session_id}: {s.query} [{s.status}]")

    # Get statistics
    stats = session_manager.get_statistics()
    print(f"\n✅ Session Statistics:")
    print(f"   Total sessions: {stats['total_sessions']}")
    print(f"   By status: {stats['by_status']}")

    print("\n" + "="*80 + "\n")


# =============================================================================
# Example 4: Integrated Workflow
# =============================================================================

async def example_integrated_workflow():
    """
    Demonstrate integrated usage of all advanced features together.

    This shows how Memory Bank, A2A Protocol, and SessionManager
    work together in a complete research workflow.
    """
    print("="*80)
    print("Example 4: Integrated Workflow")
    print("="*80)

    # Initialize all components
    memory_bank = ResearchMemoryBank(storage_dir="./memory_bank")
    protocol = ResearchCoordinationProtocol()
    session_manager = SessionManager(storage_dir="./research_sessions")

    # Step 1: Check Memory Bank for previous research
    print("\n📚 Step 1: Checking Memory Bank for previous research...")
    previous_research = memory_bank.search_memories("diabetes treatment")
    if previous_research:
        print(f"   Found {len(previous_research)} previous research sessions")
        print(f"   Latest: {previous_research[0].query}")
    else:
        print("   No previous research found, starting fresh")

    # Step 2: Create new research session
    print("\n🆕 Step 2: Creating new research session...")
    session = session_manager.create_session(
        session_id="integrated_demo_session",
        query="Diabetes medication safety profiles",
        config={"max_papers": 30}
    )
    print(f"   Session created: {session.session_id}")

    # Step 3: Coordinator uses A2A to request literature search
    print("\n📡 Step 3: Coordinator requests literature search via A2A...")
    search_msg_id = await protocol.send_research_request(
        from_agent="coordinator",
        to_agent="literature_searcher",
        query=session.query
    )
    print(f"   Request sent: {search_msg_id[:8]}...")

    # Step 4: Update session progress
    print("\n📊 Step 4: Updating session progress...")
    session_manager.update_progress(
        session.session_id,
        stage="searching",
        papers_found=30
    )

    # Step 5: Literature searcher sends results via A2A
    print("\n📥 Step 5: Receiving search results via A2A...")
    await protocol.send_research_results(
        from_agent="literature_searcher",
        to_agent="coordinator",
        results={"papers_found": 30, "papers": []},
        correlation_id=search_msg_id
    )

    # Step 6: Update progress to analysis stage
    print("\n🔬 Step 6: Moving to analysis stage...")
    session_manager.update_progress(
        session.session_id,
        stage="analyzing",
        papers_analyzed=15
    )

    # Step 7: Complete research and store in Memory Bank
    print("\n✅ Step 7: Completing research and storing in Memory Bank...")
    session_manager.complete_session(session.session_id)

    memory = ResearchMemory(
        memory_id=session.session_id,
        query=session.query,
        timestamp=datetime.now().isoformat(),
        papers_analyzed=30,
        key_findings=["Finding 1", "Finding 2", "Finding 3"],
        evidence_quality=8.0
    )
    memory_bank.store_memory(memory)
    print(f"   Research stored in Memory Bank: {memory.memory_id}")

    # Step 8: Show final statistics
    print("\n📈 Step 8: Final Statistics")
    print(f"   A2A messages sent: {protocol.get_statistics()['total_messages']}")
    print(f"   Session status: {session_manager.get_session(session.session_id).status}")
    print(f"   Memory Bank entries: {memory_bank.get_memory_summary()['total_memories']}")

    print("\n" + "="*80 + "\n")


# =============================================================================
# Main execution
# =============================================================================

if __name__ == "__main__":
    print("\n")
    print("="*80)
    print(" MedResearch AI - Advanced Features Usage Examples")
    print("="*80)
    print("\n")

    # Run synchronous examples
    example_memory_bank()
    example_session_manager()

    # Run asynchronous examples
    asyncio.run(example_a2a_protocol())
    asyncio.run(example_integrated_workflow())

    print("\n✅ All examples completed successfully!\n")
