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

"""Metrics tracking for MedResearch AI."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class ResearchMetrics:
    """Metrics for a research session."""

    session_id: str
    total_papers_searched: int = 0
    papers_analyzed: int = 0
    average_quality_score: float = 0.0
    drug_interactions_found: int = 0
    total_processing_time_ms: int = 0
    citation_accuracy_rate: float = 0.0
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = ""
    status: str = "running"

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            "session_id": self.session_id,
            "papers_searched": self.total_papers_searched,
            "papers_analyzed": self.papers_analyzed,
            "avg_quality_score": self.average_quality_score,
            "drug_interactions": self.drug_interactions_found,
            "processing_time_ms": self.total_processing_time_ms,
            "citation_accuracy": self.citation_accuracy_rate,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status
        }

    def export_json(self, filepath: str):
        """Export metrics to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


@dataclass
class AgentPerformance:
    """Performance metrics for an agent."""

    agent_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration_ms: int = 0
    average_duration_ms: float = 0.0
    last_called: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": (
                self.successful_calls / self.total_calls
                if self.total_calls > 0 else 0.0
            ),
            "total_duration_ms": self.total_duration_ms,
            "average_duration_ms": self.average_duration_ms,
            "last_called": self.last_called
        }


class MetricsTracker:
    """Track metrics across research sessions and agents."""

    def __init__(self):
        """Initialize metrics tracker."""
        self.session_metrics: Dict[str, ResearchMetrics] = {}
        self.agent_performance: Dict[str, AgentPerformance] = {}

    def start_session(self, session_id: str) -> ResearchMetrics:
        """Start tracking a new research session."""
        metrics = ResearchMetrics(session_id=session_id)
        self.session_metrics[session_id] = metrics
        return metrics

    def get_session_metrics(self, session_id: str) -> ResearchMetrics:
        """Get metrics for a session."""
        return self.session_metrics.get(session_id)

    def track_agent_call(
        self,
        agent_name: str,
        duration_ms: int,
        success: bool
    ):
        """Track an agent call."""
        if agent_name not in self.agent_performance:
            self.agent_performance[agent_name] = AgentPerformance(agent_name=agent_name)

        perf = self.agent_performance[agent_name]
        perf.total_calls += 1
        perf.successful_calls += 1 if success else 0
        perf.failed_calls += 0 if success else 1
        perf.total_duration_ms += duration_ms
        perf.average_duration_ms = perf.total_duration_ms / perf.total_calls
        perf.last_called = datetime.now().isoformat()

    def get_agent_performance(self, agent_name: str) -> AgentPerformance:
        """Get performance metrics for an agent."""
        return self.agent_performance.get(agent_name)

    def generate_report(self) -> Dict:
        """Generate comprehensive metrics report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_sessions": len(self.session_metrics),
            "active_sessions": sum(
                1 for m in self.session_metrics.values()
                if m.status == "running"
            ),
            "total_agents": len(self.agent_performance),
            "agent_performance": {
                name: perf.to_dict()
                for name, perf in self.agent_performance.items()
            },
            "recent_sessions": [
                m.to_dict()
                for m in list(self.session_metrics.values())[-5:]
            ]
        }

    def export_report(self, filepath: str):
        """Export metrics report to JSON file."""
        report = self.generate_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)


# Global metrics tracker
_global_tracker: MetricsTracker = None


def get_metrics_tracker() -> MetricsTracker:
    """Get global metrics tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = MetricsTracker()
    return _global_tracker
