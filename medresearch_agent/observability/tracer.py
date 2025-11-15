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

"""Distributed tracing for MedResearch AI."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


def setup_tracing(service_name: str = "medresearch-ai") -> trace.Tracer:
    """
    Set up OpenTelemetry tracing.

    Args:
        service_name: Name of the service

    Returns:
        Tracer instance
    """
    # Create tracer provider
    provider = TracerProvider()

    # Add console exporter for development
    processor = SimpleSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)

    # Set as global tracer provider
    trace.set_tracer_provider(provider)

    # Return tracer
    return trace.get_tracer(service_name)


# Global tracer instance
_global_tracer: trace.Tracer = None


def get_tracer(service_name: str = "medresearch-ai") -> trace.Tracer:
    """
    Get or create global tracer instance.

    Args:
        service_name: Name of the service

    Returns:
        Tracer instance
    """
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = setup_tracing(service_name)
    return _global_tracer
