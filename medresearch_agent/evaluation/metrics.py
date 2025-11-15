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

"""Evaluation metrics for MedResearch AI system."""

from dataclasses import dataclass, asdict
from typing import Dict, List
from datetime import datetime


@dataclass
class EvaluationMetrics:
    """Comprehensive evaluation metrics for a research session."""

    session_id: str
    timestamp: str

    # Citation metrics
    total_citations: int = 0
    valid_citations: int = 0
    citation_accuracy_rate: float = 0.0

    # Medical accuracy metrics
    medical_terms_found: int = 0
    terminology_score: float = 0.0

    # Evidence quality metrics
    total_papers: int = 0
    high_quality_papers: int = 0
    moderate_quality_papers: int = 0
    low_quality_papers: int = 0
    average_evidence_score: float = 0.0

    # Completeness metrics
    required_sections: int = 9
    sections_present: int = 0
    completeness_score: float = 0.0

    # Performance metrics
    processing_time_seconds: float = 0.0
    papers_per_minute: float = 0.0

    # Drug safety metrics
    drug_interactions_found: int = 0
    critical_interactions: int = 0

    # Overall quality score
    overall_quality_score: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    def calculate_overall_score(self) -> float:
        """
        Calculate overall quality score (0-100).

        Weighted average of:
        - Citation accuracy: 20%
        - Evidence quality: 30%
        - Completeness: 25%
        - Medical accuracy: 25%

        Returns:
            Overall quality score (0-100)
        """
        citation_component = self.citation_accuracy_rate * 20
        evidence_component = (self.average_evidence_score / 10) * 30
        completeness_component = self.completeness_score * 25
        terminology_component = self.terminology_score * 25

        overall = (
            citation_component +
            evidence_component +
            completeness_component +
            terminology_component
        )

        self.overall_quality_score = round(overall, 2)
        return self.overall_quality_score


def generate_evaluation_report(metrics: EvaluationMetrics) -> Dict:
    """
    Generate comprehensive evaluation report.

    Args:
        metrics: EvaluationMetrics object

    Returns:
        Dictionary with formatted evaluation report
    """
    # Calculate overall score
    metrics.calculate_overall_score()

    # Determine quality rating
    score = metrics.overall_quality_score
    if score >= 90:
        rating = "Excellent"
    elif score >= 80:
        rating = "Very Good"
    elif score >= 70:
        rating = "Good"
    elif score >= 60:
        rating = "Satisfactory"
    else:
        rating = "Needs Improvement"

    # Generate recommendations
    recommendations = []

    if metrics.citation_accuracy_rate < 0.9:
        recommendations.append(
            "Improve citation accuracy - verify all DOIs and PMIDs"
        )

    if metrics.average_evidence_score < 7.0:
        recommendations.append(
            "Include more high-quality evidence (RCTs, systematic reviews)"
        )

    if metrics.completeness_score < 0.8:
        recommendations.append(
            f"Add missing sections: {9 - metrics.sections_present} sections incomplete"
        )

    if metrics.terminology_score < 0.7:
        recommendations.append(
            "Enhance medical terminology usage and precision"
        )

    # Identify strengths
    strengths = []

    if metrics.citation_accuracy_rate >= 0.95:
        strengths.append("Excellent citation accuracy")

    if metrics.average_evidence_score >= 8.0:
        strengths.append("High-quality evidence base")

    if metrics.completeness_score >= 0.9:
        strengths.append("Comprehensive coverage of all sections")

    if metrics.critical_interactions == 0:
        strengths.append("No critical drug interactions detected")

    return {
        "session_id": metrics.session_id,
        "timestamp": metrics.timestamp,
        "overall_score": metrics.overall_quality_score,
        "rating": rating,

        "category_scores": {
            "citations": {
                "score": metrics.citation_accuracy_rate * 100,
                "details": f"{metrics.valid_citations}/{metrics.total_citations} valid"
            },
            "evidence_quality": {
                "score": (metrics.average_evidence_score / 10) * 100,
                "details": (
                    f"{metrics.high_quality_papers} high, "
                    f"{metrics.moderate_quality_papers} moderate, "
                    f"{metrics.low_quality_papers} low quality papers"
                )
            },
            "completeness": {
                "score": metrics.completeness_score * 100,
                "details": f"{metrics.sections_present}/{metrics.required_sections} sections present"
            },
            "medical_accuracy": {
                "score": metrics.terminology_score * 100,
                "details": f"{metrics.medical_terms_found} medical terms identified"
            }
        },

        "performance": {
            "processing_time": f"{metrics.processing_time_seconds:.1f}s",
            "papers_per_minute": f"{metrics.papers_per_minute:.2f}",
            "total_papers": metrics.total_papers
        },

        "safety": {
            "drug_interactions_found": metrics.drug_interactions_found,
            "critical_interactions": metrics.critical_interactions,
            "safety_status": "PASS" if metrics.critical_interactions == 0 else "REVIEW REQUIRED"
        },

        "strengths": strengths,
        "recommendations": recommendations,

        "summary": (
            f"Research quality: {rating} ({score:.1f}/100). "
            f"Analyzed {metrics.total_papers} papers with "
            f"{metrics.citation_accuracy_rate*100:.1f}% citation accuracy."
        )
    }
