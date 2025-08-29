# Copyright The OpenTelemetry Authors
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

"""Span processor for Azure Search instrumentation."""

import logging
import re
from typing import Optional
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.trace import Span
from opentelemetry.context import Context

logger = logging.getLogger(__name__)

# Semantic conventions for Azure Search
class AzureSearchAttributes:
    AZURE_SEARCH_SERVICE_NAME = "azure.search.service_name"
    AZURE_SEARCH_INDEX_NAME = "azure.search.index_name"
    AZURE_SEARCH_OPERATION = "azure.search.operation"
    AZURE_SEARCH_QUERY = "azure.search.query"
    AZURE_SEARCH_FILTER = "azure.search.filter"
    AZURE_SEARCH_RESULT_COUNT = "azure.search.result_count"
    AZURE_SEARCH_TOP = "azure.search.top"
    AZURE_SEARCH_SKIP = "azure.search.skip"


class AzureSearchSpanProcessor(SpanProcessor):
    """Span processor that enhances Azure Search spans with custom attributes."""

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
        """Called when a span is started. Add custom attributes to Azure Search spans."""
        try:
            span_name = span.name

            # Check if this is an Azure Search span
            if self._is_azure_search_span(span_name):
                self._enhance_azure_search_span(span)

        except Exception as e:
            logger.error(
                f"Error processing span in AzureSearchSpanProcessor.on_start: {e}"
            )

    def on_end(self, span: Span) -> None:
        """Called when a span is ended. Extract final attributes like result count."""
        try:
            span_name = span.name

            # Check if this is an Azure Search span
            if self._is_azure_search_span(span_name):
                self._extract_final_attributes(span)

        except Exception as e:
            logger.error(
                f"Error processing span in AzureSearchSpanProcessor.on_end: {e}"
            )

    def shutdown(self) -> None:
        """Shutdown the processor."""
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush the processor."""
        return True

    def _is_azure_search_span(self, span_name: str) -> bool:
        """Check if this is an Azure Search related span."""
        azure_search_patterns = [
            "SearchClient.search",
            "DocumentsOperations.search_post",
            "SearchClient.upload_documents",
            "SearchClient.delete_documents",
            "/indexes\\('.*'\\)/docs/search.post.search",
        ]

        for pattern in azure_search_patterns:
            if re.search(pattern, span_name):
                return True

        return False

    def _enhance_azure_search_span(self, span: Span) -> None:
        """Add custom attributes to Azure Search spans."""
        try:
            span_name = span.name
            attributes = span.attributes or {}

            # Add custom instrumentation marker
            span.set_attribute("azure.search.custom_instrumentation", "true")

            # Extract service and index information
            self._extract_service_and_index_info(span)

            # Extract search parameters
            self._extract_search_parameters(span)

            # Set operation type
            if "search" in span_name.lower():
                span.set_attribute(
                    AzureSearchAttributes.AZURE_SEARCH_OPERATION, "search"
                )
                span.set_attribute("db.operation", "search")

            elif "upload" in span_name.lower():
                span.set_attribute(
                    AzureSearchAttributes.AZURE_SEARCH_OPERATION, "upload"
                )
                span.set_attribute("db.operation", "insert")

            elif "delete" in span_name.lower():
                span.set_attribute(
                    AzureSearchAttributes.AZURE_SEARCH_OPERATION, "delete"
                )
                span.set_attribute("db.operation", "delete")

        except Exception as e:
            logger.error(f"Error enhancing Azure Search span: {e}")

    def _extract_service_and_index_info(self, span: Span) -> None:
        """Extract service name and index name from span."""
        try:
            span_name = span.name
            attributes = span.attributes or {}

            # Extract from HTTP URL if available
            if "http.url" in attributes:
                url = str(attributes["http.url"])

                if "search.windows.net" in url:
                    # Extract service name from URL like https://<service>.search.windows.net/...
                    service_match = re.search(
                        r"https://([^.]+)\.search\.windows\.net", url
                    )
                    if service_match:
                        service_name = service_match.group(1)
                        span.set_attribute(
                            AzureSearchAttributes.AZURE_SEARCH_SERVICE_NAME,
                            service_name,
                        )

                # Extract index name from URL pattern like /indexes('index')/docs/search.post.search
                index_match = re.search(r"/indexes\('([^']+)'\)", url)
                if index_match:
                    index_name = index_match.group(1)
                    span.set_attribute(
                        AzureSearchAttributes.AZURE_SEARCH_INDEX_NAME, index_name
                    )

            # Also check net.peer.name for service extraction
            if "net.peer.name" in attributes:
                peer_name = str(attributes["net.peer.name"])

                if "search.windows.net" in peer_name:
                    service_match = re.search(
                        r"([^.]+)\.search\.windows\.net", peer_name
                    )
                    if service_match:
                        service_name = service_match.group(1)
                        span.set_attribute(
                            AzureSearchAttributes.AZURE_SEARCH_SERVICE_NAME,
                            service_name,
                        )

            # Try to extract search query from request body
            if "http.request.body" in attributes:
                try:
                    import json

                    request_body = str(attributes["http.request.body"])

                    # Parse JSON request body
                    data = json.loads(request_body)
                    if isinstance(data, dict):
                        # Azure Search request body structure
                        if "search" in data:
                            query_text = str(data["search"])
                            span.set_attribute(
                                AzureSearchAttributes.AZURE_SEARCH_QUERY, query_text
                            )

                        if "top" in data:
                            span.set_attribute(
                                AzureSearchAttributes.AZURE_SEARCH_TOP, int(data["top"])
                            )

                        if "skip" in data:
                            span.set_attribute(
                                AzureSearchAttributes.AZURE_SEARCH_SKIP, int(
                                    data["skip"]
                                )
                            )

                        if "filter" in data:
                            span.set_attribute(
                                AzureSearchAttributes.AZURE_SEARCH_FILTER,
                                str(data["filter"]),
                            )

                except (json.JSONDecodeError, ValueError, KeyError, TypeError):
                    pass

            # Also try to extract from span name
            if "/indexes(" in span_name and ")" in span_name:
                index_match = re.search(r"/indexes\('([^']+)'\)", span_name)
                if index_match:
                    index_name = index_match.group(1)
                    span.set_attribute(
                        AzureSearchAttributes.AZURE_SEARCH_INDEX_NAME, index_name
                    )

        except Exception as e:
            logger.error(f"Error extracting service and index info: {e}")

    def _extract_search_parameters(self, span: Span) -> None:
        """Extract search query parameters from span attributes."""
        try:
            attributes = span.attributes or {}

            # Look for search-related attributes that might contain query information
            for attr_name, attr_value in attributes.items():
                attr_str = str(attr_name).lower()
                value_str = str(attr_value)

                # Look for query-related attributes
                if "search" in attr_str and any(
                    keyword in attr_str for keyword in ["text", "query", "term"]
                ):
                    span.set_attribute(
                        AzureSearchAttributes.AZURE_SEARCH_QUERY, value_str
                    )

                # Look for filter parameters
                elif "filter" in attr_str:
                    span.set_attribute(
                        AzureSearchAttributes.AZURE_SEARCH_FILTER, value_str
                    )

                # Look for top/limit parameters
                elif attr_str in ["top", "limit", "size"] or "top" in attr_str:
                    try:
                        top_value = int(value_str)
                        span.set_attribute(
                            AzureSearchAttributes.AZURE_SEARCH_TOP, top_value
                        )

                    except (ValueError, TypeError):
                        pass

                # Look for skip/offset parameters
                elif attr_str in ["skip", "offset"] or "skip" in attr_str:
                    try:
                        skip_value = int(value_str)
                        span.set_attribute(
                            AzureSearchAttributes.AZURE_SEARCH_SKIP, skip_value
                        )

                    except (ValueError, TypeError):
                        pass

        except Exception as e:
            logger.error(f"Error extracting search parameters: {e}")

    def _extract_from_http_span(self, span: Span) -> None:
        """Extract Azure Search details from HTTP spans (legacy method)."""
        # This method is now handled by the new extraction methods above
        pass

    def _extract_final_attributes(self, span: Span) -> None:
        """Extract final attributes when span ends (read-only span)."""
        try:
            span_name = span.name
            attributes = dict(span.attributes) if span.attributes else {}

            # Look for result count in various possible attribute names
            result_count = None
            for attr_name, attr_value in attributes.items():
                attr_str = str(attr_name).lower()

                # Common patterns for result count
                if any(
                    pattern in attr_str
                    for pattern in ["count", "total", "results", "hits"]
                ):
                    try:
                        result_count = int(attr_value)
                        break
                    except (ValueError, TypeError):
                        continue

            # Look for HTTP response body that might contain search results
            if "http.response.body" in attributes:
                try:
                    import json

                    response_body = str(attributes["http.response.body"])

                    if response_body:
                        # Try to parse as JSON to extract result count
                        data = json.loads(response_body)
                        if isinstance(data, dict):
                            # Azure Search typically returns results in different formats
                            if "value" in data and isinstance(data["value"], list):
                                result_count = len(data["value"])

                                # Note: Can't set attributes in on_end as span is read-only
                            elif "@odata.count" in data:
                                result_count = int(data["@odata.count"])

                except (json.JSONDecodeError, ValueError, KeyError, TypeError):
                    pass

            # Look for status information
            status_code = attributes.get("http.status_code")

            # Note: In on_end, spans are read-only, so we can only observe, not modify
            # All custom attributes must be set in on_start

        except Exception as e:
            logger.error(f"Error extracting final attributes: {e}")


