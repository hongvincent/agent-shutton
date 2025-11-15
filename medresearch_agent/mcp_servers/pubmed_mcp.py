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

"""PubMed MCP (Model Context Protocol) server configuration."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class PubMedMCPConfig:
    """Configuration for PubMed MCP server."""

    server_name: str = "pubmed-server"
    api_key: Optional[str] = None
    email: str = "research@medresearchai.com"
    max_results: int = 100
    timeout: int = 30

    def __post_init__(self):
        """Load API key from environment if not provided."""
        if self.api_key is None:
            self.api_key = os.getenv("PUBMED_API_KEY", "")


def create_pubmed_mcp(config: Optional[PubMedMCPConfig] = None):
    """
    Create PubMed MCP server configuration.

    This function would integrate with Google ADK's MCP system.
    Currently returns configuration dict for documentation.

    Args:
        config: PubMed MCP configuration

    Returns:
        MCP configuration dictionary
    """
    if config is None:
        config = PubMedMCPConfig()

    # MCP server configuration
    # In production, this would use:
    # from google.adk.tools import MCPTool
    #
    # pubmed_mcp = MCPTool(
    #     server_name=config.server_name,
    #     tool_name="search_pubmed",
    #     description="Search PubMed medical literature database",
    #     ...
    # )

    return {
        "server_name": config.server_name,
        "tools": [
            {
                "name": "search_pubmed",
                "description": "Search PubMed for medical literature",
                "parameters": {
                    "query": "string",
                    "max_results": "integer",
                    "sort_by": "string (relevance|date)"
                }
            },
            {
                "name": "fetch_paper_details",
                "description": "Fetch detailed information for a specific paper",
                "parameters": {
                    "pmid": "string"
                }
            },
            {
                "name": "get_related_papers",
                "description": "Get papers related to a specific PMID",
                "parameters": {
                    "pmid": "string",
                    "max_results": "integer"
                }
            }
        ],
        "config": {
            "api_key": config.api_key,
            "email": config.email,
            "max_results": config.max_results,
            "timeout": config.timeout
        }
    }


# Example MCP server configuration for ClinicalTrials.gov
CLINICAL_TRIALS_MCP_CONFIG = {
    "server_name": "clinicaltrials-server",
    "tools": [
        {
            "name": "search_trials",
            "description": "Search ClinicalTrials.gov for clinical trials",
            "parameters": {
                "condition": "string",
                "intervention": "string",
                "status": "string"
            }
        }
    ]
}

# Example MCP server configuration for DrugBank
DRUGBANK_MCP_CONFIG = {
    "server_name": "drugbank-server",
    "tools": [
        {
            "name": "check_interactions",
            "description": "Check drug-drug interactions",
            "parameters": {
                "drugs": "array of strings"
            }
        },
        {
            "name": "get_drug_info",
            "description": "Get detailed drug information",
            "parameters": {
                "drug_name": "string"
            }
        }
    ]
}
