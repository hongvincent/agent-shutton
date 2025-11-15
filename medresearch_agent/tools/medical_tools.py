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

"""Medical research tools for PubMed search, drug interactions, and validation."""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional

import requests
from Bio import Entrez


def search_pubmed(
    query: str,
    max_results: int = 50,
    sort_by: str = "relevance"
) -> Dict[str, any]:
    """
    Search PubMed for medical literature.

    Args:
        query: Search query string
        max_results: Maximum number of results to return
        sort_by: Sort order ("relevance" or "date")

    Returns:
        Dictionary with search results including paper IDs and metadata
    """
    # Set email for PubMed API (required by NCBI)
    Entrez.email = os.getenv("PUBMED_EMAIL", "research@medresearchai.com")
    api_key = os.getenv("PUBMED_API_KEY")
    if api_key:
        Entrez.api_key = api_key

    try:
        # Search PubMed
        search_handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort=sort_by
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()

        paper_ids = search_results.get("IdList", [])

        # Fetch paper details
        papers = []
        if paper_ids:
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=paper_ids,
                rettype="abstract",
                retmode="xml"
            )
            fetch_results = Entrez.read(fetch_handle)
            fetch_handle.close()

            for article in fetch_results.get("PubmedArticle", []):
                try:
                    medline = article.get("MedlineCitation", {})
                    article_data = medline.get("Article", {})

                    # Extract paper information
                    paper = {
                        "pmid": str(medline.get("PMID", "")),
                        "title": article_data.get("ArticleTitle", ""),
                        "abstract": _extract_abstract(article_data),
                        "authors": _extract_authors(article_data),
                        "journal": article_data.get("Journal", {}).get("Title", ""),
                        "pub_date": _extract_pub_date(article_data),
                        "doi": _extract_doi(article_data),
                    }
                    papers.append(paper)
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue

        return {
            "query": query,
            "total_results": len(papers),
            "papers": papers,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "error": f"PubMed search failed: {str(e)}",
            "query": query,
            "papers": []
        }


def _extract_abstract(article_data: dict) -> str:
    """Extract abstract text from article data."""
    abstract_data = article_data.get("Abstract", {})
    abstract_texts = abstract_data.get("AbstractText", [])
    if isinstance(abstract_texts, list):
        return " ".join([str(text) for text in abstract_texts])
    return str(abstract_texts) if abstract_texts else ""


def _extract_authors(article_data: dict) -> List[str]:
    """Extract author names from article data."""
    authors = []
    author_list = article_data.get("AuthorList", [])
    for author in author_list[:5]:  # Limit to first 5 authors
        last_name = author.get("LastName", "")
        initials = author.get("Initials", "")
        if last_name:
            authors.append(f"{last_name} {initials}".strip())
    return authors


def _extract_pub_date(article_data: dict) -> str:
    """Extract publication date from article data."""
    journal = article_data.get("Journal", {})
    pub_date = journal.get("JournalIssue", {}).get("PubDate", {})
    year = pub_date.get("Year", "")
    month = pub_date.get("Month", "")
    return f"{year} {month}".strip() if year else ""


def _extract_doi(article_data: dict) -> str:
    """Extract DOI from article data."""
    ids = article_data.get("ELocationID", [])
    for id_data in ids:
        if hasattr(id_data, 'attributes') and id_data.attributes.get("EIdType") == "doi":
            return str(id_data)
    return ""


def validate_medical_terminology(text: str) -> Dict[str, any]:
    """
    Validate medical terminology using basic pattern matching.

    Note: In production, this would integrate with UMLS Metathesaurus API.

    Args:
        text: Text containing medical terms to validate

    Returns:
        Dictionary with validation results
    """
    # Common medical term patterns
    medical_patterns = [
        r'\b[A-Z]{2,}\b',  # Acronyms (e.g., COPD, HIV)
        r'\b\w+itis\b',  # Inflammation terms
        r'\b\w+osis\b',  # Condition terms
        r'\b\w+ectomy\b',  # Surgical procedures
        r'\b\w+pathy\b',  # Disease terms
    ]

    found_terms = set()
    for pattern in medical_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found_terms.update(matches)

    return {
        "text_length": len(text),
        "medical_terms_found": len(found_terms),
        "terms": list(found_terms)[:20],  # Limit to first 20
        "validation_score": min(1.0, len(found_terms) / 10),  # Simple score
    }


def check_drug_interactions(drug_list: List[str]) -> Dict[str, any]:
    """
    Check for drug-drug interactions.

    Note: This is a placeholder. In production, integrate with DrugBank API.

    Args:
        drug_list: List of drug names to check

    Returns:
        Dictionary with interaction warnings
    """
    # Known interaction pairs (simplified for demo)
    known_interactions = {
        ("warfarin", "aspirin"): "Increased bleeding risk",
        ("metformin", "alcohol"): "Increased risk of lactic acidosis",
        ("simvastatin", "grapefruit"): "Increased statin levels",
    }

    interactions = []
    drug_list_lower = [d.lower() for d in drug_list]

    for (drug1, drug2), warning in known_interactions.items():
        if drug1 in drug_list_lower and drug2 in drug_list_lower:
            interactions.append({
                "drug1": drug1,
                "drug2": drug2,
                "severity": "moderate",
                "warning": warning
            })

    return {
        "drugs_checked": drug_list,
        "interactions_found": len(interactions),
        "interactions": interactions,
        "safe": len(interactions) == 0
    }


def calculate_evidence_quality(
    study_type: str,
    sample_size: int,
    has_control_group: bool = False,
    peer_reviewed: bool = True
) -> Dict[str, any]:
    """
    Calculate evidence quality score for a research study.

    Args:
        study_type: Type of study (RCT, cohort, case-control, case-report)
        sample_size: Number of participants
        has_control_group: Whether study has control group
        peer_reviewed: Whether study is peer-reviewed

    Returns:
        Dictionary with quality score and rating
    """
    # Base scores by study type
    type_scores = {
        "rct": 9.0,  # Randomized Controlled Trial
        "systematic_review": 10.0,
        "meta_analysis": 10.0,
        "cohort": 7.0,
        "case_control": 6.0,
        "case_series": 4.0,
        "case_report": 3.0,
        "expert_opinion": 2.0
    }

    base_score = type_scores.get(study_type.lower().replace(" ", "_"), 5.0)

    # Adjust for sample size
    if sample_size >= 1000:
        sample_modifier = 1.0
    elif sample_size >= 100:
        sample_modifier = 0.8
    elif sample_size >= 50:
        sample_modifier = 0.6
    else:
        sample_modifier = 0.4

    # Adjust for control group
    control_modifier = 1.1 if has_control_group else 1.0

    # Adjust for peer review
    peer_modifier = 1.0 if peer_reviewed else 0.7

    # Calculate final score (0-10 scale)
    final_score = base_score * sample_modifier * control_modifier * peer_modifier
    final_score = min(10.0, max(0.0, final_score))

    # Determine rating
    if final_score >= 8.0:
        rating = "High Quality"
    elif final_score >= 6.0:
        rating = "Moderate Quality"
    elif final_score >= 4.0:
        rating = "Low Quality"
    else:
        rating = "Very Low Quality"

    return {
        "score": round(final_score, 2),
        "rating": rating,
        "study_type": study_type,
        "sample_size": sample_size,
        "has_control_group": has_control_group,
        "peer_reviewed": peer_reviewed
    }


def save_research_report(report_content: str, filename: str) -> Dict[str, any]:
    """
    Save research report to a file.

    Args:
        report_content: Content of the research report
        filename: Name of file to save (without extension)

    Returns:
        Dictionary with save status
    """
    try:
        # Ensure reports directory exists
        reports_dir = "research_reports"
        os.makedirs(reports_dir, exist_ok=True)

        # Add .md extension if not present
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        filepath = os.path.join(reports_dir, filename)

        # Save the report
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return {
            "success": True,
            "filepath": filepath,
            "filename": filename,
            "size_bytes": len(report_content.encode('utf-8'))
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def extract_paper_metadata(paper_text: str) -> Dict[str, any]:
    """
    Extract metadata from paper text using pattern matching.

    Args:
        paper_text: Full text or abstract of paper

    Returns:
        Dictionary with extracted metadata
    """
    metadata = {
        "has_statistics": False,
        "has_methods_section": False,
        "has_results_section": False,
        "word_count": 0,
        "citation_count_estimate": 0
    }

    # Count words
    metadata["word_count"] = len(paper_text.split())

    # Check for sections
    metadata["has_methods_section"] = bool(
        re.search(r'\b(methods?|methodology)\b', paper_text, re.IGNORECASE)
    )
    metadata["has_results_section"] = bool(
        re.search(r'\b(results?|findings?)\b', paper_text, re.IGNORECASE)
    )

    # Check for statistical content
    stats_patterns = [r'p\s*[<>=]\s*0\.\d+', r'\bp-value\b', r'\bconfidence interval\b']
    metadata["has_statistics"] = any(
        re.search(pattern, paper_text, re.IGNORECASE)
        for pattern in stats_patterns
    )

    # Estimate citations (rough count of references)
    citation_patterns = [r'\[\d+\]', r'\(\d{4}\)', r'et al\.']
    metadata["citation_count_estimate"] = sum(
        len(re.findall(pattern, paper_text))
        for pattern in citation_patterns
    )

    return metadata
