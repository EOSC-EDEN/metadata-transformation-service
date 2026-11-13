"""Cross-schema examples exercise each input/output representation through the API."""

import io
import json

import pytest
from conftest import ROOT
from lxml import etree

CASES = json.loads((ROOT / "examples/combinations.json").read_text())


def semantic_xml(text):
    return [
        (n.tag, dict(n.attrib), (n.text or "").strip())
        for n in etree.fromstring(text.encode()).iter()
    ]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["output"])
def test_cross_schema_combinations(client, case):
    response = client.post(
        "/api/v1/transform",
        data={
            "source_schema": case["source"],
            "target_schema": case["target"],
            "input_format": case["input_format"],
            "output_format": case["output_format"],
            "file": (
                io.BytesIO((ROOT / "examples/inputs" / case["input"]).read_bytes()),
                case["input"],
            ),
        },
    )
    assert response.status_code == 200, response.json
    expected = (ROOT / "examples/outputs" / case["output"]).read_text()
    parse = json.loads if case["output_format"] == "json" else semantic_xml
    assert parse(response.json["metadata"]) == parse(expected)
    report = response.json["report"]
    assert report["schema_transformation"] is True
    assert report["serialization_transformation"] == (
        case["input_format"] == "json" or case["output_format"] == "json"
    )
    assert report["steps"][-1]["status"] == "passed"


@pytest.mark.parametrize("metadata", ["{", "{}", '{"unknown": []}'])
def test_json_input_validation(client, metadata):
    response = client.post(
        "/api/v1/transform",
        json={
            "source_schema": "datacite-4.1",
            "target_schema": "oai-dc",
            "input_format": "json",
            "output_format": "json",
            "metadata": metadata,
        },
    )
    assert response.status_code == 422
    assert response.json["error"]["stage"] == "source_validation"


def test_repeated_language_tagged_titles(client):
    data = json.loads((ROOT / "examples/inputs/datacite.json").read_text())
    data["titles"].append({"title": 'Café & "data"', "lang": "nl"})
    response = client.post(
        "/api/v1/transform",
        json={
            "source_schema": "datacite-4.1",
            "target_schema": "oai-dc",
            "input_format": "json",
            "output_format": "json",
            "metadata": json.dumps(data),
        },
    )
    assert response.status_code == 200
    dc = json.loads(response.json["metadata"])
    assert dc["title"][1] == 'Café & "data"'
    assert "language" not in dc
    assert any(
        "Language annotations" in warning
        for warning in response.json["report"]["warnings"]
    )
    reverse = client.post(
        "/api/v1/transform",
        json={
            "source_schema": "oai-dc",
            "target_schema": "datacite-4.1",
            "input_format": "json",
            "output_format": "json",
            "metadata": json.dumps(dc),
        },
    )
    assert reverse.status_code == 200
    assert json.loads(reverse.json["metadata"])["titles"] == [
        {"title": t["title"]} for t in data["titles"]
    ]


def test_json_to_xml_missing_target_field(client):
    dc = json.loads((ROOT / "examples/inputs/dublincore.json").read_text())
    del dc["creator"]
    response = client.post(
        "/api/v1/transform",
        json={
            "source_schema": "oai-dc",
            "target_schema": "datacite-4.1",
            "input_format": "json",
            "output_format": "xml",
            "metadata": json.dumps(dc),
        },
    )
    assert response.status_code == 422
    assert response.json["error"]["stage"] == "target_validation"


@pytest.mark.parametrize("value", [None, 42, {}, {"value": "nested"}, ["valid", 5], []])
def test_flat_dc_invalid_values(client, value):
    dc = json.loads((ROOT / "examples/inputs/dublincore.json").read_text())
    dc["title"] = value
    response = client.post(
        "/api/v1/transform",
        json={
            "metadata": json.dumps(dc),
            "source_schema": "oai-dc",
            "target_schema": "datacite-4.1",
            "input_format": "json",
            "output_format": "xml",
        },
    )
    assert response.status_code == 422
    assert response.json["error"]["stage"] == "source_validation"


def test_flat_dc_singleton_arrays(client):
    dc = json.loads((ROOT / "examples/inputs/dublincore.json").read_text())
    response = client.post(
        "/api/v1/transform",
        json={
            "metadata": json.dumps({k: [v] for k, v in dc.items()}),
            "source_schema": "oai-dc",
            "target_schema": "datacite-4.1",
            "input_format": "json",
            "output_format": "json",
        },
    )
    assert response.status_code == 200
    assert json.loads(response.json["metadata"])["titles"] == [
        {"title": "Example research dataset"}
    ]
    assert not any(
        "Language annotations" in w for w in response.json["report"]["warnings"]
    )


def test_flat_dc_scalar_and_language_warning(client, metadata):
    response = client.post(
        "/api/v1/transform",
        json={
            "metadata": metadata,
            "source_schema": "datacite-4.1",
            "target_schema": "oai-dc",
            "input_format": "xml",
            "output_format": "json",
        },
    )
    assert response.status_code == 200
    dc = json.loads(response.json["metadata"])
    assert dc["title"] == "Example research dataset"
    assert isinstance(dc["creator"], str)
    assert "language" not in dc
    assert any("Language annotations" in w for w in response.json["report"]["warnings"])
