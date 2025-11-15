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

"""Structured logging for MedResearch AI."""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class MedResearchLogger:
    """Structured logger for MedResearch AI system."""

    def __init__(self, name: str = "medresearch", level: str = "INFO"):
        """
        Initialize logger.

        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        self.logger.handlers = []

        # Console handler with JSON formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(console_handler)

        # File handler for persistent logs
        file_handler = logging.FileHandler('medresearch.log')
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(file_handler)

    def _format_log(
        self,
        level: str,
        message: str,
        event_type: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format log entry as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
        }

        if event_type:
            log_entry["event_type"] = event_type

        if data:
            log_entry["data"] = data

        return json.dumps(log_entry)

    def debug(self, message: str, event_type: Optional[str] = None, **kwargs):
        """Log debug message."""
        self.logger.debug(self._format_log("DEBUG", message, event_type, kwargs))

    def info(self, message: str, event_type: Optional[str] = None, **kwargs):
        """Log info message."""
        self.logger.info(self._format_log("INFO", message, event_type, kwargs))

    def warning(self, message: str, event_type: Optional[str] = None, **kwargs):
        """Log warning message."""
        self.logger.warning(self._format_log("WARNING", message, event_type, kwargs))

    def error(self, message: str, event_type: Optional[str] = None, **kwargs):
        """Log error message."""
        self.logger.error(self._format_log("ERROR", message, event_type, kwargs))

    def critical(self, message: str, event_type: Optional[str] = None, **kwargs):
        """Log critical message."""
        self.logger.critical(self._format_log("CRITICAL", message, event_type, kwargs))

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log structured event."""
        self.info(f"Event: {event_type}", event_type=event_type, **data)


# Global logger instance
_global_logger: Optional[MedResearchLogger] = None


def get_logger(name: str = "medresearch", level: str = "INFO") -> MedResearchLogger:
    """
    Get or create global logger instance.

    Args:
        name: Logger name
        level: Log level

    Returns:
        MedResearchLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = MedResearchLogger(name, level)
    return _global_logger
