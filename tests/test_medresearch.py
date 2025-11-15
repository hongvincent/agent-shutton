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

"""Integration tests for MedResearch AI."""

import pytest
from medresearch_agent.tools.medical_tools import (
    search_pubmed,
    validate_medical_terminology,
    check_drug_interactions,
    calculate_evidence_quality,
)


class TestMedicalTools:
    """Test medical research tools."""

    def test_search_pubmed(self):
        """Test PubMed search functionality."""
        result = search_pubmed("diabetes mellitus", max_results=5)

        assert "query" in result
        assert "papers" in result
        assert result["query"] == "diabetes mellitus"
        # May fail if no API key, but structure should be correct
        assert isinstance(result["papers"], list)

    def test_validate_medical_terminology(self):
        """Test medical terminology validation."""
        text = "The patient presented with COPD and hypertension requiring atenolol therapy."

        result = validate_medical_terminology(text)

        assert "text_length" in result
        assert "medical_terms_found" in result
        assert "validation_score" in result
        assert result["validation_score"] >= 0.0
        assert result["validation_score"] <= 1.0

    def test_check_drug_interactions(self):
        """Test drug interaction checking."""
        drugs = ["warfarin", "aspirin"]

        result = check_drug_interactions(drugs)

        assert "drugs_checked" in result
        assert "interactions_found" in result
        assert "interactions" in result
        assert "safe" in result
        assert result["drugs_checked"] == drugs
        # This combination should show interaction
        assert result["interactions_found"] > 0

    def test_calculate_evidence_quality(self):
        """Test evidence quality calculation."""
        result = calculate_evidence_quality(
            study_type="RCT",
            sample_size=1000,
            has_control_group=True,
            peer_reviewed=True
        )

        assert "score" in result
        assert "rating" in result
        assert "study_type" in result
        assert result["score"] >= 0.0
        assert result["score"] <= 10.0
        assert result["rating"] in ["High Quality", "Moderate Quality", "Low Quality", "Very Low Quality"]

    def test_evidence_quality_rct_vs_case_report(self):
        """Test that RCTs score higher than case reports."""
        rct_score = calculate_evidence_quality(
            study_type="RCT",
            sample_size=500,
            has_control_group=True
        )

        case_report_score = calculate_evidence_quality(
            study_type="case_report",
            sample_size=10,
            has_control_group=False
        )

        assert rct_score["score"] > case_report_score["score"]


class TestObservability:
    """Test observability components."""

    def test_logger_initialization(self):
        """Test logger can be initialized."""
        from medresearch_agent.observability import get_logger

        logger = get_logger()
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")

    def test_metrics_tracker(self):
        """Test metrics tracker."""
        from medresearch_agent.observability import get_metrics_tracker

        tracker = get_metrics_tracker()
        assert tracker is not None

        # Start a session
        metrics = tracker.start_session("test-session-123")
        assert metrics.session_id == "test-session-123"
        assert metrics.total_papers_searched == 0

        # Track agent call
        tracker.track_agent_call("test_agent", 100, True)

        # Generate report
        report = tracker.generate_report()
        assert "total_sessions" in report
        assert "agent_performance" in report


class TestConfiguration:
    """Test configuration."""

    def test_config_loading(self):
        """Test configuration loads correctly."""
        from medresearch_agent.config import config

        assert config is not None
        assert config.coordinator_model == "gemini-2.0-flash-exp"
        assert config.max_papers_per_search > 0
        assert config.max_loop_iterations > 0


@pytest.mark.asyncio
class TestAPI:
    """Test FastAPI endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from api.main import app

        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_start_research(self, client):
        """Test research session creation."""
        request_data = {
            "query": "latest treatments for hypertension",
            "time_frame_years": 5,
            "max_papers": 20
        }

        response = client.post("/research", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "initiated"
        assert "message" in data

    def test_get_research_status(self, client):
        """Test getting research status."""
        # First create a session
        request_data = {
            "query": "diabetes treatments",
            "max_papers": 10
        }

        create_response = client.post("/research", json=request_data)
        session_id = create_response.json()["session_id"]

        # Then check status
        status_response = client.get(f"/research/{session_id}")

        assert status_response.status_code == 200
        data = status_response.json()
        assert data["session_id"] == session_id
        assert "status" in data
        assert "progress" in data

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get("/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "total_sessions" in data
        assert "agent_performance" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
