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

"""Literature search agents for PubMed and other medical databases."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ..config import config
from ..tools.medical_tools import search_pubmed


# PubMed search agent
pubmed_searcher = Agent(
    name="pubmed_searcher",
    model=config.worker_model,
    description="Searches PubMed database for medical literature",
    instruction="""
    You are a PubMed search specialist. Your role is to:

    1. Take a medical research query and search the PubMed database
    2. Use the search_pubmed tool to find relevant papers
    3. Return a structured list of papers with metadata

    Focus on:
    - Recent publications (last 5 years preferred)
    - High-impact journals
    - Peer-reviewed articles
    - Relevant to the research query

    Return the search results in a clear, structured format.
    """,
    tools=[FunctionTool(search_pubmed)]
)


# ClinicalTrials.gov searcher (placeholder - would use real API)
clinical_trials_searcher = Agent(
    name="clinical_trials_searcher",
    model=config.worker_model,
    description="Searches ClinicalTrials.gov for ongoing and completed clinical trials",
    instruction="""
    You are a clinical trials research specialist. Your role is to:

    1. Search ClinicalTrials.gov for relevant clinical trials
    2. Find both ongoing and completed trials
    3. Extract key information about trial design, status, and results

    For each trial, include:
    - NCT number
    - Trial title
    - Status (recruiting, completed, etc.)
    - Phase
    - Intervention/treatment
    - Primary outcomes

    Note: Currently using simulated data. In production, integrate with ClinicalTrials.gov API.
    """,
    tools=[]  # Would add ClinicalTrials API tool here
)


# Google Scholar searcher (placeholder)
scholar_searcher = Agent(
    name="scholar_searcher",
    model=config.worker_model,
    description="Searches Google Scholar for academic publications",
    instruction="""
    You are a Google Scholar search specialist. Your role is to:

    1. Search Google Scholar for academic medical publications
    2. Find highly-cited papers and systematic reviews
    3. Include preprints and conference proceedings

    Focus on:
    - Citation count (higher is better)
    - Systematic reviews and meta-analyses
    - Recent publications
    - Authoritative sources

    Note: Currently using simulated data. In production, integrate with Google Scholar API.
    """,
    tools=[]  # Would add Google Scholar tool here
)


# Parallel literature searcher - coordinates all search agents
# Note: This would use ParallelAgent in production ADK
parallel_literature_searcher = Agent(
    name="parallel_literature_searcher",
    model=config.worker_model,
    description="Coordinates parallel searches across multiple medical databases",
    instruction="""
    You are a medical literature search coordinator. Your role is to:

    1. Receive a research query from the main coordinator
    2. Delegate searches to specialized search agents:
       - PubMed searcher for peer-reviewed medical literature
       - ClinicalTrials searcher for clinical trial data
       - Scholar searcher for broader academic coverage

    3. Aggregate results from all sources
    4. Remove duplicates based on DOI/PMID
    5. Rank results by relevance and quality

    Return a comprehensive list of unique papers from all sources, prioritizing:
    - Recent publications
    - High-impact journals
    - Systematic reviews and RCTs
    - Papers with clear methodology

    Format the output as a structured list with all metadata.
    """,
    sub_agents=[
        pubmed_searcher,
        clinical_trials_searcher,
        scholar_searcher
    ],
    tools=[FunctionTool(search_pubmed)]
)
