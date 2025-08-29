"""
Azure AI Search instrumentation for OpenTelemetry.
"""

import logging
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from .version import __version__

logger = logging.getLogger(__name__)

_instruments = ("azure-search-documents >= 11.0.0, < 12.0.0",)


class AzureSearchInstrumentor(BaseInstrumentor):
    """An instrumentor for Azure AI Search"""

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        """Enable instrumentation for Azure Search clients using span processor approach."""
        try:
            from .span_processor import (
                AzureSearchSpanProcessor,
            )

            from opentelemetry import trace

            # Get the tracer provider and add our custom span processor
            tracer_provider = trace.get_tracer_provider()

            if hasattr(tracer_provider, "add_span_processor"):
                processor = AzureSearchSpanProcessor()
                tracer_provider.add_span_processor(processor)
                logger.info("Azure Search span processor instrumentation enabled")
            else:
                logger.warning("TracerProvider doesn't support span processors")

            # Add method wrapping to capture search queries and results
            from .wrappers import (
                _wrap_search_client_methods,
            )

            _wrap_search_client_methods()

        except ImportError as e:
            logger.warning(f"Azure Search span processor not found: {e}")
        except Exception as e:
            logger.error(f"Failed to add Azure Search span processor: {e}")

    def _uninstrument(self, **kwargs):
        """Disable instrumentation for Azure Search clients."""
        try:
            # Remove method wrapping
            from .wrappers import (
                _unwrap_search_client_methods,
            )

            _unwrap_search_client_methods()

            # Note: Span processors are typically managed by the TracerProvider
            # and don't need explicit removal in most cases
            logger.info("Azure Search instrumentation disabled")

        except Exception as e:
            logger.error(f"Failed to uninstrument Azure Search: {e}")


