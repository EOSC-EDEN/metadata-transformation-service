# Extending a deployment

## New schemas and crosswalks

Add local schemas and catalog entries. Schema IDs are not hardcoded in the core.
Each schema used by a crosswalk needs an XML validation schema because crosswalks
follow an XML → XML execution convention. Other representations are optional:

```json
{
  "id": "my-record-v1",
  "version": "1.0",
  "formats": {
    "xml": "schemas/my-record.xsd",
    "json": "schemas/my-record.json"
  }
}
```

Register a mapping with no serialization fields or format names:

```json
{
  "id": "my-record-to-dc",
  "version": "1.0.0",
  "source_schema": "my-record-v1",
  "target_schema": "oai-dc",
  "path": "crosswalks/my-record-to-dc.xsl",
  "notes": ["Describe mapping coverage and assumptions here."]
}
```

Notes are descriptive provenance, not warnings. Use `xsl:message` for issues
encountered during a particular transformation. The engine is inferred from the
stylesheet root. Do not add supported format lists to this entry: discovery
computes them from the available converters and configured representations.
The same mapping can serve XML and JSON clients without duplicate entries.

## Representation converters

Converters operate within one schema and explicitly declare formats:

```json
{
  "id": "my-record-json-to-xml",
  "version": "1.0.0",
  "schema": "my-record-v1",
  "input_format": "json",
  "output_format": "xml",
  "path": "converters/my-record-json-to-xml.xsl",
  "notes": []
}
```

Supply validators for both representations. JSON-input XSLT accepts a `json-text`
parameter and named `main` template; XML input starts with the document node.
Converters can execute directly when the request's schema IDs match, even in a
deployment with no schema crosswalks. Register one converter per schema/format
pair. Crosswalk execution uses at most one conversion before and after it.

The bundled JSON adapters are only examples for DataCite and Dublin Core.
Other schemas supply their own stylesheets, optionally sharing their own helpers.

## New formats and engines

A format registration supplies a media type and a schema compiler. The compiler
returns a callable that validates text, raising `ValueError` for invalid content.
For example, a simple format whose schema file contains a minimum line count:

```python
from mts.api import create_app
from mts.config import Config
from mts.core.formats import Format, default_formats


def compile_lines(path):
    minimum = int(path.read_text())

    def validate(content):
        if len(content.splitlines()) < minimum:
            raise ValueError("Too few lines")

    return validate


class LinesEngine:
    input_formats = {"lines"}

    def accepts(self, path):
        return path.read_text() == "uppercase-lines"

    def transform(self, metadata, operation):
        return metadata.upper(), []


formats = {
    **default_formats(),
    "lines": Format("text/plain", compile_lines),
    "lines-upper": Format("text/plain", compile_lines),
}
app = create_app(Config(), formats=formats, engines=[LinesEngine()])
```

For this example, configure a converter from `lines` to `lines-upper`, with
`uppercase-lines` as its resource file, and validation files for both formats.
To retain Saxon alongside this engine, pass `[XsltEngine(), LinesEngine()]`.
A schema crosswalk still follows the XML convention; a new client format needs
converters connecting that format with XML to use schema crosswalks.

All resources and implementation extensions are trusted deployment inputs;
remote executable uploads are not enabled. Transport remains UTF-8 text.
See `tests/test_extensions.py` for executable custom format/converter examples.
