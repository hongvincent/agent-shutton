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

"""Drug interaction checking with validation loop."""

from google.adk.agents import Agent, BaseAgent
from google.adk.runners import EventActions
from google.adk.tools import FunctionTool

from ..config import config
from ..tools.medical_tools import check_drug_interactions


class DrugInteractionValidator(BaseAgent):
    """Validator for drug interaction checking results."""

    def __init__(self):
        super().__init__(
            name="drug_interaction_validator",
            model=config.analysis_model,
            description="Validates drug interaction check results"
        )

    async def run(self, state: dict) -> EventActions:
        """
        Validate drug interaction results.

        Escalates if validation passes, otherwise retry.
        """
        # Check if drug interactions were properly analyzed
        if not state.get("drug_list"):
            # No drugs found, validation fails - retry extraction
            return EventActions(escalate=False)

        interaction_results = state.get("interaction_results", {})

        # Validate that check was performed
        if not interaction_results:
            return EventActions(escalate=False)

        # Validate results structure
        if "drugs_checked" not in interaction_results:
            return EventActions(escalate=False)

        # Validation passed - escalate to continue
        return EventActions(escalate=True)


# Drug extractor agent
drug_extractor = Agent(
    name="drug_extractor",
    model=config.analysis_model,
    description="Extracts drug names and medications from research papers",
    instruction="""
    You are a pharmaceutical terminology specialist. Your role is to:

    1. Analyze research papers to extract all mentioned drugs and medications
    2. Identify:
       - Generic drug names
       - Brand names
       - Drug classes
       - Dosages (if mentioned)
       - Routes of administration

    3. Normalize drug names to standard nomenclature
    4. Remove duplicates
    5. Return a clean list of unique drugs

    Be thorough and accurate in drug name extraction.
    Output the drug list in your response.
    """,
    tools=[]
)


# Interaction checker agent
interaction_checker = Agent(
    name="interaction_checker",
    model=config.analysis_model,
    description="Checks for drug-drug interactions using medical databases",
    instruction="""
    You are a drug interaction specialist. Your role is to:

    1. Take a list of drugs from the drug extractor
    2. Use check_drug_interactions tool to identify potential interactions
    3. Assess interaction severity:
       - Critical: Contraindicated combination
       - Moderate: Use with caution
       - Minor: Minimal clinical significance

    4. For each interaction found, provide:
       - Drugs involved
       - Interaction mechanism
       - Clinical significance
       - Management recommendations

    5. Prioritize by severity (critical first)

    Be thorough and evidence-based. Patient safety is paramount.
    """,
    tools=[FunctionTool(check_drug_interactions)]
)


# Drug Interaction Loop Agent
# Note: This would use LoopAgent with validator in production
drug_interaction_checker = Agent(
    name="drug_interaction_checker",
    model=config.analysis_model,
    description="Validates drug safety through iterative checking with retry logic",
    instruction="""
    You are a drug safety coordinator. Your role is to:

    1. Receive analyzed papers that mention drugs or medications
    2. Extract all drug names from the papers
    3. Check for potential drug-drug interactions
    4. Validate results to ensure no false negatives on critical interactions
    5. Retry extraction/checking if validation fails (max 3 attempts)

    Process flow:
    1. Extract drugs → drug_extractor
    2. Check interactions → interaction_checker
    3. Validate → DrugInteractionValidator
    4. If validation fails, retry from step 1
    5. If validation passes, return results

    Critical safety note:
    - Better to over-report potential interactions than miss critical ones
    - Always err on the side of caution
    - Clearly mark severity levels

    Output format:
    {
      "drugs_found": ["drug1", "drug2", ...],
      "interactions": [
        {
          "drugs": ["drug1", "drug2"],
          "severity": "critical|moderate|minor",
          "mechanism": "...",
          "recommendation": "..."
        }
      ],
      "safe": true|false
    }
    """,
    sub_agents=[
        drug_extractor,
        interaction_checker
    ],
    tools=[FunctionTool(check_drug_interactions)]
)
