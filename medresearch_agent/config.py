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

"""Configuration for MedResearch AI agents and tools."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MedResearchConfig:
    """Configuration for MedResearch AI system."""

    # Model Configuration
    coordinator_model: str = "gemini-2.0-flash-exp"
    worker_model: str = "gemini-2.0-flash-exp"
    analysis_model: str = "gemini-1.5-pro"

    # API Keys
    google_api_key: Optional[str] = None
    drugbank_api_key: Optional[str] = None
    pubmed_api_key: Optional[str] = None

    # Agent Configuration
    max_papers_per_search: int = 50
    max_loop_iterations: int = 3
    analysis_timeout_seconds: int = 300

    # Memory Configuration
    enable_memory_bank: bool = True
    memory_embedding_model: str = "text-embedding-004"

    # Observability Configuration
    enable_logging: bool = True
    enable_tracing: bool = True
    enable_metrics: bool = True
    log_level: str = "INFO"

    # Session Configuration
    session_storage_dir: str = "./research_sessions"
    enable_pause_resume: bool = True

    # Deployment Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8080

    def __post_init__(self):
        """Load API keys from environment if not provided."""
        self.google_api_key = self.google_api_key or os.getenv("GOOGLE_API_KEY")
        self.drugbank_api_key = self.drugbank_api_key or os.getenv("DRUGBANK_API_KEY")
        self.pubmed_api_key = self.pubmed_api_key or os.getenv("PUBMED_API_KEY")

        # Ensure session directory exists
        os.makedirs(self.session_storage_dir, exist_ok=True)


# Global configuration instance
config = MedResearchConfig()
