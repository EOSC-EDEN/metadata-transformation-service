# API demos: DataCite ↔ Dublin Core, XML and JSON

From the project root, start `flask --app mts.api:create_app run`.
Run the following commands in a second Bash terminal. Every response contains
serialized metadata plus the validation and transformation report. Schema IDs
and JSON profiles remain those documented in the README.

## datacite-4.1 XML → oai-dc JSON

```bash
curl -s http://127.0.0.1:5000/api/v1/transform \
  -F source_schema=datacite-4.1 \
  -F target_schema=oai-dc \
  -F input_format=xml \
  -F output_format=json \
  -F file=@examples/inputs/datacite.xml \
  | python -m json.tool
```

Expected output metadata: `examples/outputs/datacite-to-dc-xml-to-json.json`.

## datacite-4.1 JSON → oai-dc XML

```bash
curl -s http://127.0.0.1:5000/api/v1/transform \
  -F source_schema=datacite-4.1 \
  -F target_schema=oai-dc \
  -F input_format=json \
  -F output_format=xml \
  -F file=@examples/inputs/datacite.json \
  | python -m json.tool
```

Expected output metadata: `examples/outputs/datacite-to-dc-json-to-xml.xml`.

## datacite-4.1 JSON → oai-dc JSON

```bash
curl -s http://127.0.0.1:5000/api/v1/transform \
  -F source_schema=datacite-4.1 \
  -F target_schema=oai-dc \
  -F input_format=json \
  -F output_format=json \
  -F file=@examples/inputs/datacite.json \
  | python -m json.tool
```

Expected output metadata: `examples/outputs/datacite-to-dc-json-to-json.json`.

## oai-dc XML → datacite-4.1 JSON

```bash
curl -s http://127.0.0.1:5000/api/v1/transform \
  -F source_schema=oai-dc \
  -F target_schema=datacite-4.1 \
  -F input_format=xml \
  -F output_format=json \
  -F file=@examples/inputs/dublincore.xml \
  | python -m json.tool
```

Expected output metadata: `examples/outputs/dc-to-datacite-xml-to-json.json`.

## oai-dc JSON → datacite-4.1 XML

```bash
curl -s http://127.0.0.1:5000/api/v1/transform \
  -F source_schema=oai-dc \
  -F target_schema=datacite-4.1 \
  -F input_format=json \
  -F output_format=xml \
  -F file=@examples/inputs/dublincore.json \
  | python -m json.tool
```

Expected output metadata: `examples/outputs/dc-to-datacite-json-to-xml.xml`.

## oai-dc JSON → datacite-4.1 JSON

```bash
curl -s http://127.0.0.1:5000/api/v1/transform \
  -F source_schema=oai-dc \
  -F target_schema=datacite-4.1 \
  -F input_format=json \
  -F output_format=json \
  -F file=@examples/inputs/dublincore.json \
  | python -m json.tool
```

Expected output metadata: `examples/outputs/dc-to-datacite-json-to-json.json`.


## Conversion without a schema change

```bash
curl -s http://127.0.0.1:5000/api/v1/transform \
  -F source_schema=oai-dc \
  -F target_schema=oai-dc \
  -F input_format=json \
  -F output_format=xml \
  -F file=@examples/inputs/dublincore.json \
  | python -m json.tool
```

This returns `report.crosswalk: null` and one entry in `report.conversions`.
Swap formats and use `dublincore.xml` for the reverse. Use `datacite-4.1` and
its corresponding example inputs for DataCite conversion.

All cross-schema examples above select one of the same two mappings, regardless
of input/output formats. You can explicitly add `-F crosswalk_id=datacite-to-dc`
to every DataCite → DC request (or `dc-to-datacite` in reverse).
Browse http://127.0.0.1:5000/api/v1/converters to inspect direct conversions.
