# Metadata Transformation Service

The Metadata Transformation Service (MTS) transforms metadata between different metadata schemas, schema versions, and serialization formats.

The MTS provides a reusable interface for metadata transformation using managed metadata crosswalks. This supports interoperability between repository systems, preservation services, and other research data infrastructure.

## Overview

The Metadata Transformation Service enables clients to submit metadata for transformation and specify the required source and target metadata representations.

Transformations may include:

* transformation between metadata schemas;
* transformation between different versions of a schema;
* transformation between serialization formats such as JSON and XML; and
* transformations using metadata crosswalks registered and managed by external services such as the Metadata Schema and Crosswalk Registry (MSCR).

## Documentation

An MkDocs documentation site is available; its Markdown sources are in [docs/](docs/).

* [Metadata Transformation Service specification](docs/specification.md)
* [Contributing guidelines](CONTRIBUTING.md)
* [License](LICENSE)

A [terminal recording](https://asciinema.org/a/U8jpOHfFFKAGphsN) shows the current API capabilities including metadata transformations.

## Run with Docker Compose

From the project directory:

```bash
docker compose up --build -d
curl http://localhost:5000/health
curl http://localhost:5000/api/v1/crosswalks
docker compose logs -f mts
# Stop the service:
docker compose down
```

The single container runs Gunicorn as a non-root user. The API is published on
localhost port 5000. Resources are mounted read-only from `./resources` so you
can edit the catalog or mappings and run `docker compose restart mts` to reload. Rebuild after changing Python code or dependencies. 

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python examples/transform.py
flask --app mts.api:create_app run
```

The Flask development server listens at http://127.0.0.1:5000. For deployment,
use a production WSGI server behind HTTPS. The project is a prototype, not a
complete implementation of every requirement in the supplied specification.

## Development checks

```bash
pytest
ruff check .
ruff format --check .
python -m build
```

Tests cover actual example outputs, source/target validation, unsupported and
ambiguous requests, repeated values, language inference, size limits, and both
API submission methods. `docs/architecture.md` explains the extension points.
`docs/specification.md` contains the supplied requirements.

## Transform a file

```bash
curl http://127.0.0.1:5000/api/v1/transform \
  -F source_schema=datacite-4.1 \
  -F target_schema=oai-dc \
  -F file=@examples/inputs/datacite.xml
```

For the reverse example, use source `oai-dc`, target `datacite-4.1`, and
`examples/inputs/dublincore.xml`. For XML → JSON, use source and target
`datacite-4.1`, `output_format=json`, and `examples/inputs/datacite.xml`.

Text submission uses the same endpoint with an `application/json` body:

```json
{
  "metadata": "<resource xmlns=\"http://datacite.org/schema/kernel-4\">...</resource>",
  "source_schema": "datacite-4.1",
  "target_schema": "oai-dc",
  "input_format": "xml",
  "output_format": "xml"
}
```

The abbreviated metadata above is illustrative. Use the complete bundled input
for an executable request. `crosswalk_id` is optional; ambiguous matches fail
rather than picking an arbitrary version. Responses contain `metadata` as a
serialized string, its `media_type`, and a structured `report`. JSON metadata
is also returned as a string, keeping one response shape for both output types.
A failed target validation returns an error and report, without output metadata.

`GET /health`, `/api/v1/schemas`, `/api/v1/crosswalks`, `/api/v1/converters`, and
`/api/v1/capabilities` provide discovery. The contract is in `docs/openapi.yaml`.

## Core use without Flask

```python
from pathlib import Path
from mts.config import Config
from mts.core.models import TransformationRequest
from mts.core.transformation import TransformationService

service = TransformationService(Config(resource_path=Path("resources")))
result = service.transform(
    TransformationRequest(
        metadata=Path("examples/inputs/datacite.xml").read_text(),
        source_schema="datacite-4.1",
        target_schema="oai-dc",
    )
)
print(result.metadata)
print(result.report)
```

## Configuration

`src/mts/config.py` defines the `Config` dataclass. Pass it explicitly or use
`Config.from_env()` (the Flask factory default). Supported environment overrides:

| Variable | Default | Meaning |
|---|---|---|
| MTS_RESOURCE_PATH | resources | Local catalog, schemas, and stylesheets |
| MTS_MAX_METADATA_BYTES | 1000000 | UTF-8 metadata byte limit in both core and API |
| MTS_MAX_REQUEST_BYTES | 2000000 | Whole HTTP body limit, including upload/envelope overhead |

Relative resource paths are resolved against the process working directory.
Resources are deliberately operator-managed and external to the installed Python
package. Keep the supplied resource directory or point to another one when
installing the wheel elsewhere. All schemas are loaded locally, without runtime downloads.

## Example coverage and limitations

* DataCite 4.1 XML → Simple Dublin Core in an OAI-DC wrapper.
* OAI-DC XML → DataCite 4.1 XML.
* DataCite 4.1 XML → a **minimal, Invenio-shaped JSON profile**.
* DataCite ↔ Dublin Core with XML → JSON, JSON → XML, and JSON → JSON.

See `docs/api-demos.md` for commands and `examples/combinations.json` for all
additional examples. Run `python examples/transform.py` to generate all outputs.
Set `input_format=json` when uploading a JSON record.

Dublin Core JSON is a flat local representation: each of the fifteen DC terms
accepts a string or a nonempty array of strings. Output uses a string for one
value and an array for multiple values; missing terms are omitted. Unknown keys,
nested objects, numbers, nulls and empty arrays are rejected.

Per-value XML language annotations are omitted with a transformation warning.
The `language` element describes the resource language and is not inferred from
those annotations. This representation is not JSON-LD or a mandated DCMI JSON
encoding. DataCite JSON keeps its separate, documented minimal representation.

The XML schema is pinned to 4.1 to match the user's reference example, not to
claim that 4.1 is the newest DataCite version. The JSON profile follows the
identifier, creators, titles, publisher, publicationYear and resourceType
shapes in the linked Invenio example. It is **not the full Invenio or official
DataCite JSON schema**, and does not accept their full examples. The converter
rejects unsupported fields/attributes. DataCite JSON titles retain language attributes;
metadata control attributes such as xsi:schemaLocation are omitted.

The DC crosswalks map only the six fields above. Their notes describe omitted
fields and qualifiers; notes do not imply a runtime warning for every record. For DC → DataCite, supply exactly one DOI,
publisher, YYYY date, and DataCite general resource type. Creators and titles
must also be present to pass target validation. The example does not invent
missing values. Arbitrary DC records need a richer crosswalk.

XSD validation checks structure and datatypes, not complete semantic correctness
or DOI registration. DC uses the OAI wrapper schema with a local implementation
of Simple DC literal elements; see `resources/schemas/README.md`.

## Add or edit a crosswalk

1. Add an XSLT stylesheet under `resources/crosswalks/`.
2. Add its catalog entry with a unique ID, version, source/target schema IDs,
   relative path, and optional descriptive `notes`.
3. Restart the app to load the catalog and infer the engine.
4. Add representative input/output fixtures and tests.

There is **no language or engine field**. XSLT is recognized from its root
namespace and `stylesheet`/`transform` element, not the filename. SaxonC executes
both mappings and converters.

## Output format is independent of the crosswalk

There are two schema mappings: `datacite-to-dc` and `dc-to-datacite`.
Crosswalks follow an XML → XML execution convention. Their catalog entries contain
no format fields, and their names contain no serialization formats. Selection
uses the schema pair and optional ID, not the API request's formats.

Four separate converters handle XML ↔ JSON within each schema. They are listed
under `converters` in the catalog and live in `resources/converters/`. A request
may use one input converter, the schema crosswalk, and one output converter.
All four XML/JSON combinations use the same crosswalk ID per schema direction.
No conversion chains or route search are used. If a required direct converter
is unavailable, the request fails with `no_converter` before execution.

Same-schema requests execute a direct converter, or validate and return the
input when the formats also match. To deliberately execute a same-schema
normalization crosswalk, specify its `crosswalk_id` explicitly.

The report identifies `crosswalk` (null for conversion-only requests) and each
executed entry in `conversions`. `serialization_transformation` means a converter
ran: it can be true for JSON → JSON when XML is used internally. Input, converted
input, native crosswalk output, and final output are validated at their relevant
boundaries. Converters emit warnings for deliberate information loss, including
language annotations omitted from flat DC JSON.

Only trusted, operator-managed stylesheets are executed. Users can author their
own stylesheets for an operator to register. Remote stylesheet upload/editing is
not exposed yet: it needs access control and isolated execution with file,
network and resource restrictions. Incoming metadata DTDs/entities are rejected,
but this is not a sandbox for untrusted executable stylesheets.


## Add your own schemas and formats

Schemas and their XML/JSON representation files are catalog data, not hardcoded
Python classes. Add your schema files and versioned catalog entry, then register
a matching stylesheet. No core/API edits are needed. New schemas can use their
own XSLT directly: the bundled DataCite/DC adapters are examples, not a requirement.

For new serialization formats, register a `Format` with a media type and schema
compiler, and use an engine capable of reading the input. The app factory and
core service accept `formats=` and `engines=`. Discovery lists configured schema formats, derived crosswalk capabilities, and direct
converters. Together these describe the available request combinations. See `docs/extensions.md` for examples.

Adding a format name alone does not provide parsing or conversion. Extensions
are trusted deployment code/resources; this does not enable remote schema,
format, or stylesheet upload. Current transport carries UTF-8 text, not binary
formats. The JSON envelope for API responses is independent of metadata format.

## Derived crosswalk capabilities and notes

`GET /api/v1/crosswalks` returns `supported_input_formats` and
`supported_output_formats`, computed from direct converters for the source and
target schemas. XML is supported directly. JSON input needs a source-schema
JSON → XML converter; JSON output needs a target-schema XML → JSON converter.
Both representations must have configured validators. These lists can differ;
they are computed, not authored in `catalog.json`. Startup validates the resource
and engine configuration before any capabilities are published.

`notes` describe mapping coverage, assumptions, or other information. They are
returned by discovery and under `report.crosswalk.notes` (or each converter's
provenance). Only messages emitted during execution populate `report.warnings`
and produce `success_with_warnings`. Mapping notes alone yield `success`.
Automatic detection of every unmapped element is not implemented.