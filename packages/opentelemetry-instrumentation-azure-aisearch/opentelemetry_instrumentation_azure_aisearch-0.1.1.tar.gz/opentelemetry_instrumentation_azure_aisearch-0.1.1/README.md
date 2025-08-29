## OpenTelemetry Instrumentation for Azure AI Search

An OpenTelemetry instrumentation package for `azure-search-documents` that enriches spans for Azure AI Search (formerly Azure Cognitive Search). It adds useful attributes like service/index names, search text, filters, pagination parameters, document counts, and samples of top results, for both sync and async clients.

### Features
- **Automatic wrapping** of `SearchClient.search`, `upload_documents`, and `delete_documents` (sync and async)
- **Span enrichment** with:
  - `azure.search.service_name`
  - `azure.search.index_name`
  - `azure.search.operation` (search/upload/delete)
  - `azure.search.query`, `azure.search.filter`, `azure.search.top`, `azure.search.skip`
  - `azure.search.document_count` (for upload/delete)
  - `azure.search.result_count` and a small sampled payload in `azure.search.result`
- **Span processor** adds additional context when spans start/end

## Requirements
- Python >= 3.8
- `azure-search-documents >= 11.0.0`
- OpenTelemetry Python API/SDK 1.20+/0.45b0 semantic conventions (see `pyproject.toml`)

## Installation

### From PyPI
```bash
pip install opentelemetry-instrumentation-azure-aisearch
```

### From source
```bash
pip install .
```

## Quickstart

### Configure a tracer/exporter (example: OTLP to localhost)
```python
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

resource = Resource.create({"service.name": "azure-search-sample"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")))
trace.set_tracer_provider(provider)
```

### Enable instrumentation
```python
from opentelemetry.instrumentation.azure_aisearch import AzureSearchInstrumentor

AzureSearchInstrumentor().instrument()
```

### Use the Azure Search client (sync)
```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<your-service>.search.windows.net"
index_name = "<your-index>"
api_key = "<your-key>"

client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))

# A search operation (spans will be created and enriched automatically)
results = client.search(search_text="notebook", top=5, filter="category eq 'electronics'")
for doc in results:
    # Iterate to allow the wrapper to count and sample results
    pass
```

### Use the Azure Search client (async)
```python
import asyncio
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential

async def main():
    client = SearchClient(
        endpoint="https://<your-service>.search.windows.net",
        index_name="<your-index>",
        credential=AzureKeyCredential("<your-key>")
    )

    results = await client.search(search_text="laptop", top=3)
    async for doc in results:
        pass

asyncio.run(main())
```

## What this instrumentation adds
- For search spans:
  - `db.operation="search"`
  - `azure.search.operation="search"`
  - `azure.search.service_name`, `azure.search.index_name`
  - `azure.search.query`, `azure.search.filter`, `azure.search.top`, `azure.search.skip`
  - `azure.search.result_count` when iteration completes
  - `azure.search.result` with a JSON of up to the first 3 sampled results (truncated). Vector-like fields (e.g., `embedding`, `vector`, or long numeric arrays) are excluded from samples.
- For upload/delete spans:
  - `db.operation` set to `insert`/`delete`
  - `azure.search.operation="upload_documents"` or `"delete_documents"`
  - `azure.search.document_count` with the number of documents passed

Notes:
- Service/index names are derived from client internals (`_endpoint`, `_index_name`) or HTTP attributes.
- The span processor also attempts to parse HTTP request/response bodies when available to extract query and counts.

## Configuration
This package does not currently expose runtime config flags. Behavior is:
- Sampling of up to 3 results is always on for search spans (stored in `azure.search.result`).
- Result count is set when iteration completes or when async iteration finishes.

Exporter configuration can be done via OpenTelemetry environment variables, for example:
```bash
export OTEL_SERVICE_NAME=azure-search-sample
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

## Disabling
```python
from opentelemetry.instrumentation.azure_aisearch import AzureSearchInstrumentor

AzureSearchInstrumentor().uninstrument()
```

## Version compatibility
- Azure SDK: `azure-search-documents` 11.x
- OpenTelemetry: tested with `opentelemetry-api ~= 1.20`, `opentelemetry-instrumentation ~= 0.45b0`, `opentelemetry-semantic-conventions ~= 0.45b0`

## Limitations and cautions
- The `azure.search.result` attribute stores a small sample of search results to aid debugging and analytics. These samples may contain sensitive data. Consider your data governance policies before enabling in production.
- Attributes rely on Azure SDK internals and HTTP span attributes which may vary across SDK versions.
- The span processor cannot add attributes in `on_end` (spans are read-only then); final counts are inferred and logged but not set at end time by the processor. Counts are set via the wrapper when iteration completes.

## Contributing
Issues and PRs are welcome. Please ensure style and linting match OpenTelemetry Python conventions. The project uses `hatchling` for builds.

## License
Apache-2.0. See `LICENSE` if present, or the license header in source files.
