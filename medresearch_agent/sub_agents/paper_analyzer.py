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

"""Sequential paper analysis pipeline."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ..config import config
from ..tools.medical_tools import (
    extract_paper_metadata,
    calculate_evidence_quality,
    validate_medical_terminology
)


# Stage 1: Metadata Extraction
metadata_extractor = Agent(
    name="metadata_extractor",
    model=config.worker_model,
    description="Extracts structured metadata from research papers",
    instruction="""
    You are a metadata extraction specialist. Your role is to:

    1. Analyze paper text (title, abstract, full text if available)
    2. Extract key metadata:
       - Authors and affiliations
       - Publication date and journal
       - DOI and PMID
       - Keywords and MeSH terms
       - Study type (RCT, cohort, case-control, etc.)
       - Sample size

    3. Use extract_paper_metadata tool to identify structural elements
    4. Return structured metadata in consistent format

    Be precise and thorough in extraction.
    """,
    tools=[FunctionTool(extract_paper_metadata)]
)


# Stage 2: Methodology Analyzer
methodology_analyzer = Agent(
    name="methodology_analyzer",
    model=config.analysis_model,  # Use more powerful model for analysis
    description="Analyzes research methodology and study design",
    instruction="""
    You are a research methodology expert. Your role is to:

    1. Analyze the study design and methodology
    2. Identify:
       - Study type (RCT, observational, etc.)
       - Sample size and population
       - Inclusion/exclusion criteria
       - Intervention details
       - Control group design
       - Outcome measures
       - Statistical methods

    3. Assess methodology quality and potential biases
    4. Note any limitations or concerns

    Provide a clear, structured analysis of the methodology.
    """,
    tools=[]
)


# Stage 3: Findings Extractor
findings_extractor = Agent(
    name="findings_extractor",
    model=config.analysis_model,
    description="Extracts key findings and results from research papers",
    instruction="""
    You are a research findings specialist. Your role is to:

    1. Extract key findings from the results section
    2. Identify:
       - Primary outcomes and their statistical significance
       - Secondary outcomes
       - Adverse events or side effects
       - Subgroup analyses
       - Effect sizes and confidence intervals

    3. Note the clinical significance (not just statistical)
    4. Extract exact quotes for important findings

    Provide clear, concise summaries of the key results.
    """,
    tools=[FunctionTool(validate_medical_terminology)]
)


# Stage 4: Limitations Analyzer
limitations_analyzer = Agent(
    name="limitations_analyzer",
    model=config.analysis_model,
    description="Identifies study limitations and potential biases",
    instruction="""
    You are a critical appraisal specialist. Your role is to:

    1. Identify study limitations:
       - Sample size issues
       - Selection bias
       - Confounding factors
       - Measurement errors
       - Generalizability concerns

    2. Assess potential biases:
       - Funding sources
       - Conflicts of interest
       - Publication bias
       - Reporting bias

    3. Note what the authors themselves identified as limitations
    4. Identify limitations they may have missed

    Provide an objective, thorough assessment of limitations.
    """,
    tools=[]
)


# Stage 5: Quality Scorer
quality_scorer = Agent(
    name="quality_scorer",
    model=config.analysis_model,
    description="Rates the overall quality and strength of evidence",
    instruction="""
    You are an evidence quality assessor. Your role is to:

    1. Rate the overall quality of evidence using established criteria
    2. Consider:
       - Study design (RCT > cohort > case-control > case series)
       - Sample size and statistical power
       - Methodology rigor
       - Bias assessment
       - Consistency with other studies
       - Directness of evidence

    3. Use calculate_evidence_quality tool to generate objective score
    4. Provide a final quality rating: High, Moderate, Low, or Very Low

    5. Justify the rating with specific criteria

    Be objective and evidence-based in your assessment.
    """,
    tools=[FunctionTool(calculate_evidence_quality)]
)


# Sequential Paper Analyzer - orchestrates the pipeline
# Note: This would use SequentialAgent in production ADK
sequential_paper_analyzer = Agent(
    name="sequential_paper_analyzer",
    model=config.analysis_model,
    description="Coordinates sequential analysis pipeline for research papers",
    instruction="""
    You are a research paper analysis coordinator. Your role is to:

    1. Receive papers from the literature search results
    2. Process each paper through a 5-stage sequential pipeline:

       Stage 1: Extract metadata → metadata_extractor
       Stage 2: Analyze methodology → methodology_analyzer
       Stage 3: Extract key findings → findings_extractor
       Stage 4: Identify limitations → limitations_analyzer
       Stage 5: Rate evidence quality → quality_scorer

    3. Compile comprehensive analysis for each paper
    4. Return structured analysis results

    Process papers systematically and thoroughly. Each stage builds on the previous.

    Output format for each paper:
    {
      "paper_id": "PMID or DOI",
      "metadata": {...},
      "methodology": {...},
      "findings": {...},
      "limitations": [...],
      "quality_score": {...}
    }
    """,
    sub_agents=[
        metadata_extractor,
        methodology_analyzer,
        findings_extractor,
        limitations_analyzer,
        quality_scorer
    ],
    tools=[
        FunctionTool(extract_paper_metadata),
        FunctionTool(calculate_evidence_quality),
        FunctionTool(validate_medical_terminology)
    ]
)
