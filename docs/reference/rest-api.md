# REST API

The Metadata Transformation Service (MTS) provides a REST API for transforming metadata between schemas and serialization formats.

All endpoints are relative to the service root (e.g. `http://localhost:5000`). The API accepts metadata as a file upload or as a JSON request body. Responses are returned in JSON, with transformed metadata included as a serialized string.

The API contract is defined in the [OpenAPI specification](https://github.com/EOSC-EDEN/metadata-transformation-service/blob/main/docs/openapi.yaml).

## Transformation

| Endpoint | Description |
|---|---|
| `POST /api/v1/transform` | Transform one metadata record between schemas, schema versions, and/or serialization formats. Accepts a file upload (`multipart/form-data`) or a JSON request body (`application/json`). |

The following parameters are supported:

| Parameter | Required | Description |
|---|---|---|
| `file` / `metadata` | Yes | Input metadata, supplied as an uploaded file or a serialized string in a JSON request. |
| `source_schema` | Yes | Identifier of the source metadata schema (e.g. `datacite-4.1`). |
| `target_schema` | Yes | Identifier of the target metadata schema (e.g. `oai-dc`). |
| `input_format` | No | Input serialization format (e.g. `xml` or `json`). Defaults to `xml`. |
| `output_format` | No | Output serialization format (e.g. `xml` or `json`). Defaults to `xml`. |
| `crosswalk_id` | No | Identifier of a specific crosswalk to use. When omitted, the service selects a suitable crosswalk if an unambiguous match is available. |

For example, to transform DataCite XML metadata to Dublin Core JSON:

```bash
curl http://localhost:5000/api/v1/transform \
  -F source_schema=datacite-4.1 \
  -F target_schema=oai-dc \
  -F input_format=xml \
  -F output_format=json \
  -F file=@examples/inputs/datacite.xml
```

The service also supports serialization conversion without changing the metadata schema by specifying the same source and target schema.

See the [API examples](https://github.com/EOSC-EDEN/metadata-transformation-service/blob/main/docs/api-demos.md) for additional examples.

## Service information

| Endpoint | Description |
|---|---|
| `GET /health` | Service health check. |
| `GET /api/v1/schemas` | List available metadata schemas and their supported formats. |
| `GET /api/v1/crosswalks` | List available metadata crosswalks, including their source and target schemas, versions, supported formats, and notes. |
| `GET /api/v1/converters` | List available serialization converters and their supported schemas and formats. |
| `GET /api/v1/capabilities` | Retrieve service capabilities, including supported input/output formats and configured limits. |

## Responses

Successful transformations return `200 OK` with the transformed metadata and a structured report.

The response includes:

| Field | Description |
|---|---|
| `metadata` | Transformed metadata as a serialized string (XML or JSON). |
| `media_type` | Media type of the output metadata. |
| `report.status` | Transformation status (`success` or `success_with_warnings`). |
| `report.crosswalk` | Information about the applied crosswalk, or `null` if no crosswalk was needed. |
| `report.steps` | Information about the transformation steps performed. |
| `report.warnings` | Warnings generated during the transformation. |
| `report.schema_transformation` | Whether a schema transformation was performed. |
| `report.serialization_transformation` | Whether serialization conversion was performed. |
| `report.conversions` | Information about serialization conversions performed. |

## Errors

Invalid requests or failed transformations return a JSON error response containing an `error` object and a transformation `report`.

| HTTP status | Description |
|---|---|
| `400 Bad Request` | Invalid or unsupported transformation request. |
| `413 Content Too Large` | Request exceeds the configured size limits. |
| `415 Unsupported Media Type` | Unsupported request content type. |
| `422 Unprocessable Content` | Source validation, transformation, or target validation failed. |
| `500 Internal Server Error` | Unexpected service error. |

The `error` object contains a `code`, a `message`, and optionally a `stage` identifying where the failure occurred.