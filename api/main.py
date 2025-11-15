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

"""FastAPI backend for MedResearch AI deployment."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from medresearch_agent.config import config
from medresearch_agent.observability import get_logger, get_metrics_tracker

# Initialize FastAPI app
app = FastAPI(
    title="MedResearch AI API",
    description="Intelligent Multi-Agent System for Medical Literature Review",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize observability
logger = get_logger()
metrics_tracker = get_metrics_tracker()

# In-memory session storage (in production, use database)
research_sessions: Dict[str, dict] = {}


# Request/Response Models
class ResearchRequest(BaseModel):
    """Request model for starting a research session."""

    query: str = Field(..., description="Medical research query")
    time_frame_years: int = Field(5, description="Number of years to search back")
    include_observational: bool = Field(True, description="Include observational studies")
    max_papers: int = Field(50, description="Maximum number of papers to analyze")
    check_drug_interactions: bool = Field(True, description="Check for drug interactions")


class ResearchResponse(BaseModel):
    """Response model for research session."""

    session_id: str
    status: str
    message: str
    created_at: str


class SessionStatus(BaseModel):
    """Status model for research session."""

    session_id: str
    status: str
    progress: dict
    results: Optional[dict] = None
    created_at: str
    updated_at: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: str


# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with API information."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/research", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new research session.

    This endpoint initiates a comprehensive medical literature review based on the query.
    The research runs asynchronously in the background.
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())

        # Create session record
        session = {
            "session_id": session_id,
            "query": request.query,
            "status": "initiated",
            "progress": {
                "stage": "initializing",
                "papers_found": 0,
                "papers_analyzed": 0,
                "current_step": "Setting up research session"
            },
            "config": request.dict(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "results": None
        }

        research_sessions[session_id] = session

        # Start metrics tracking
        metrics_tracker.start_session(session_id)

        # Log event
        logger.log_event("research_started", {
            "session_id": session_id,
            "query": request.query,
            "max_papers": request.max_papers
        })

        # Add background task to run research
        # Note: In production, this would call the actual agent
        background_tasks.add_task(run_research_session, session_id, request)

        return {
            "session_id": session_id,
            "status": "initiated",
            "message": f"Research session started for query: '{request.query}'",
            "created_at": session["created_at"]
        }

    except Exception as e:
        logger.error(f"Failed to start research session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start research: {str(e)}")


@app.get("/research/{session_id}", response_model=SessionStatus)
async def get_research_status(session_id: str):
    """
    Get the status of a research session.

    Returns current progress and results if completed.
    """
    if session_id not in research_sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    session = research_sessions[session_id]

    return SessionStatus(**session)


@app.post("/research/{session_id}/pause")
async def pause_research(session_id: str):
    """
    Pause an ongoing research session.

    The session can be resumed later from the same point.
    """
    if session_id not in research_sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    session = research_sessions[session_id]

    if session["status"] != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pause session in status: {session['status']}"
        )

    session["status"] = "paused"
    session["updated_at"] = datetime.now().isoformat()

    logger.log_event("research_paused", {"session_id": session_id})

    return {"session_id": session_id, "status": "paused"}


@app.post("/research/{session_id}/resume")
async def resume_research(session_id: str, background_tasks: BackgroundTasks):
    """
    Resume a paused research session.
    """
    if session_id not in research_sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    session = research_sessions[session_id]

    if session["status"] != "paused":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume session in status: {session['status']}"
        )

    session["status"] = "running"
    session["updated_at"] = datetime.now().isoformat()

    logger.log_event("research_resumed", {"session_id": session_id})

    # Resume background task
    # In production, this would resume the agent from checkpoint
    background_tasks.add_task(resume_research_session, session_id)

    return {"session_id": session_id, "status": "resumed"}


@app.delete("/research/{session_id}")
async def delete_research(session_id: str):
    """
    Delete a research session and its data.
    """
    if session_id not in research_sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    del research_sessions[session_id]

    logger.log_event("research_deleted", {"session_id": session_id})

    return {"session_id": session_id, "status": "deleted"}


@app.get("/metrics")
async def get_metrics():
    """
    Get system-wide metrics.

    Returns performance data and statistics across all research sessions.
    """
    try:
        report = metrics_tracker.generate_report()
        return report
    except Exception as e:
        logger.error(f"Failed to generate metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


# Background Tasks

async def run_research_session(session_id: str, request: ResearchRequest):
    """
    Run the research session in the background.

    This is a placeholder. In production, this would:
    1. Initialize the agent runner
    2. Execute the research workflow
    3. Update session progress
    4. Store results
    """
    try:
        session = research_sessions[session_id]
        session["status"] = "running"

        # Simulate research stages (in production, call actual agent)
        stages = [
            ("searching", "Searching medical databases..."),
            ("analyzing", "Analyzing papers..."),
            ("synthesizing", "Synthesizing evidence..."),
            ("generating", "Generating report..."),
            ("evaluating", "Validating results..."),
        ]

        for stage, message in stages:
            session["progress"]["stage"] = stage
            session["progress"]["current_step"] = message
            session["updated_at"] = datetime.now().isoformat()

            # In production, this would be actual agent execution
            # For now, just update status

        # Mark as completed
        session["status"] = "completed"
        session["progress"]["stage"] = "completed"
        session["progress"]["current_step"] = "Research completed"
        session["results"] = {
            "summary": f"Research completed for: {request.query}",
            "report_path": f"research_reports/session_{session_id}.md"
        }
        session["updated_at"] = datetime.now().isoformat()

        logger.log_event("research_completed", {"session_id": session_id})

    except Exception as e:
        logger.error(f"Research session {session_id} failed: {str(e)}")
        session["status"] = "failed"
        session["progress"]["current_step"] = f"Error: {str(e)}"
        session["updated_at"] = datetime.now().isoformat()


async def resume_research_session(session_id: str):
    """
    Resume a paused research session.

    In production, this would load the checkpoint and continue from there.
    """
    logger.log_event("resuming_research", {"session_id": session_id})
    # Implementation would resume from checkpoint


# Main entry point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True,
        log_level="info"
    )
