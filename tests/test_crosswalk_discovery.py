"""Derived capabilities and descriptive notes stay separate from execution warnings."""

import pytest
from conftest import ROOT

from mts.core.models import TransformationRequest


def test_clean_crosswalk_definition(client):
    items = client.get("/api/v1/crosswalks").json["crosswalks"]
    assert {c["id"] for c in items} == {"datacite-to-dc", "dc-to-datacite"}
    for c in items:
        assert "input_format" not in c and "output_format" not in c
        assert "warnings" not in c and c["notes"]
        assert c["supported_input_formats"] == ["json", "xml"]
        assert c["supported_output_formats"] == ["json", "xml"]


def test_asymmetric_support(service):
    mapping = service.catalog.crosswalks[0]
    service.catalog.converters = [
        c
        for c in service.catalog.converters
        if not (c.schema == "oai-dc" and c.output_format == "json")
    ]
    supported = service.catalog.supported_formats(mapping)
    assert supported["supported_input_formats"] == ["json", "xml"]
    assert supported["supported_output_formats"] == ["xml"]


def test_no_converters_means_xml_only(service):
    service.catalog.converters = []
    assert service.catalog.supported_formats(service.catalog.crosswalks[0]) == {
        "supported_input_formats": ["xml"],
        "supported_output_formats": ["xml"],
    }


def test_notes_do_not_make_warnings(service, metadata):
    result = service.transform(
        TransformationRequest(metadata, "datacite-4.1", "oai-dc")
    )
    assert result.report["status"] == "success"
    assert result.report["warnings"] == []
    assert result.report["crosswalk"]["notes"]


def test_runtime_warning_still_reported(service, metadata):
    result = service.transform(
        TransformationRequest(metadata, "datacite-4.1", "oai-dc", output_format="json")
    )
    assert result.report["status"] == "success_with_warnings"
    assert any("Language annotations" in w for w in result.report["warnings"])
    assert not any("Maps identifier" in w for w in result.report["warnings"])


@pytest.mark.parametrize(
    "inf,out", [("xml", "xml"), ("xml", "json"), ("json", "xml"), ("json", "json")]
)
def test_every_advertised_pair(client, inf, out):
    for c in client.get("/api/v1/crosswalks").json["crosswalks"]:
        stem = "datacite" if c["source_schema"] == "datacite-4.1" else "dublincore"
        response = client.post(
            "/api/v1/transform",
            json={
                "metadata": (ROOT / f"examples/inputs/{stem}.{inf}").read_text(),
                "source_schema": c["source_schema"],
                "target_schema": c["target_schema"],
                "crosswalk_id": c["id"],
                "input_format": inf,
                "output_format": out,
            },
        )
        assert response.status_code == 200, response.json
