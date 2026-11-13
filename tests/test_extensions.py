"""Exercise independent schemas and formats without changing core/API code."""

import json

import pytest

from mts.api import create_app
from mts.config import Config
from mts.core.formats import Format, default_formats


def catalog(root, fmt, schema, mapping):
    """Create a deployment with one custom schema and one mapping."""
    (root / "schema.txt").write_text(schema)
    (root / "mapping.txt").write_text(mapping)
    (root / "catalog.json").write_text(
        json.dumps(
            {
                "schemas": [
                    {
                        "id": "custom",
                        "version": "1",
                        "formats": {fmt: "schema.txt", fmt + "-upper": "schema.txt"},
                    }
                ],
                "crosswalks": [],
                "converters": [
                    {
                        "id": "custom",
                        "version": "1",
                        "schema": "custom",
                        "input_format": fmt,
                        "output_format": fmt + "-upper",
                        "path": "mapping.txt",
                    }
                ],
            }
        )
    )


def submit(client, metadata, fmt):
    return client.post(
        "/api/v1/transform",
        json={
            "metadata": metadata,
            "source_schema": "custom",
            "target_schema": "custom",
            "input_format": fmt,
            "output_format": fmt + "-upper",
        },
    )


def test_custom_json_schema(tmp_path):
    schema = {
        "type": "object",
        "required": ["name"],
        "properties": {"name": {"type": "string"}},
        "additionalProperties": False,
    }
    catalog(
        tmp_path,
        "json",
        json.dumps(schema),
        """
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <xsl:output method="json"/><xsl:param name="json-text"/>
 <xsl:template name="main">
  <xsl:sequence select="map {'name': upper-case(parse-json($json-text)?name)}"/>
 </xsl:template>
</xsl:stylesheet>""",
    )
    client = create_app(
        Config(resource_path=tmp_path),
        formats={**default_formats(), "json-upper": default_formats()["json"]},
    ).test_client()
    result = submit(client, '{"name":"Marcella"}', "json")
    assert result.status_code == 200
    assert json.loads(result.json["metadata"]) == {"name": "MARCELLA"}
    assert client.get("/api/v1/capabilities").json["input_formats"] == [
        "json",
        "json-upper",
    ]
    assert client.get("/api/v1/schemas").json["schemas"][0]["id"] == "custom"


def compile_lines(path):
    """Custom schema: minimum number of lines."""
    minimum = int(path.read_text())

    def validate(content):
        if len(content.splitlines()) < minimum:
            raise ValueError("Too few lines")

    return validate


class LinesEngine:
    """Illustrative engine for an independently registered text format."""

    input_formats = {"lines"}

    def accepts(self, path):
        return path.read_text() == "uppercase-lines"

    def transform(self, metadata, crosswalk):
        return metadata.upper(), []


def test_custom_format_engine_and_discovery(tmp_path):
    catalog(tmp_path, "lines", "2", "uppercase-lines")
    client = create_app(
        Config(resource_path=tmp_path),
        formats={
            "lines": Format("text/plain", compile_lines),
            "lines-upper": Format("text/plain", compile_lines),
        },
        engines=[LinesEngine()],
    ).test_client()
    result = submit(client, "one\ntwo", "lines")
    assert result.status_code == 200
    assert result.json["metadata"] == "ONE\nTWO"
    assert result.json["media_type"] == "text/plain"
    info = client.get("/api/v1/capabilities").json
    assert info["input_formats"] == info["output_formats"] == ["lines", "lines-upper"]
    assert info["media_types"]["lines"] == "text/plain"
    invalid = submit(client, "one", "lines")
    assert invalid.status_code == 422
    assert invalid.json["error"]["stage"] == "source_validation"


def test_missing_format_registration(tmp_path):
    catalog(tmp_path, "lines", "2", "uppercase-lines")
    with pytest.raises(ValueError, match="Unregistered catalog format"):
        create_app(Config(resource_path=tmp_path))


def test_engine_cannot_read_format(tmp_path):
    catalog(
        tmp_path,
        "lines",
        "2",
        """<xsl:stylesheet version="3.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"/>""",
    )
    with pytest.raises(ValueError, match="Engine cannot read lines"):
        create_app(
            Config(resource_path=tmp_path),
            formats={
                "lines": Format("text/plain", compile_lines),
                "lines-upper": Format("text/plain", compile_lines),
            },
        )
