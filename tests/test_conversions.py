"""Conversions surround one schema mapping, independently of API formats."""

import json
from dataclasses import replace

import pytest
from conftest import ROOT

from mts.core.exceptions import TransformationError
from mts.core.models import TransformationRequest


@pytest.mark.parametrize(
    "source,target,filename,crosswalk",
    [
        ("datacite-4.1", "oai-dc", "datacite", "datacite-to-dc"),
        ("oai-dc", "datacite-4.1", "dublincore", "dc-to-datacite"),
    ],
)
@pytest.mark.parametrize(
    "inf,out", [("xml", "xml"), ("xml", "json"), ("json", "xml"), ("json", "json")]
)
def test_one_crosswalk_for_all_formats(
    service, source, target, filename, crosswalk, inf, out
):
    req = TransformationRequest(
        (ROOT / f"examples/inputs/{filename}.{inf}").read_text(),
        source,
        target,
        input_format=inf,
        output_format=out,
        crosswalk_id=crosswalk,
    )
    result = service.transform(req)
    assert result.report["crosswalk"]["id"] == crosswalk
    assert len(result.report["conversions"]) == int(inf == "json") + int(out == "json")
    assert result.report["serialization_transformation"] == bool(
        result.report["conversions"]
    )
    assert result.report["steps"][-1]["stage"] == "target_validation"


@pytest.mark.parametrize(
    "schema,filename", [("datacite-4.1", "datacite"), ("oai-dc", "dublincore")]
)
@pytest.mark.parametrize("inf,out", [("xml", "json"), ("json", "xml")])
def test_same_schema_conversion(service, schema, filename, inf, out):
    req = TransformationRequest(
        (ROOT / f"examples/inputs/{filename}.{inf}").read_text(),
        schema,
        schema,
        input_format=inf,
        output_format=out,
    )
    result = service.transform(req)
    assert result.report["crosswalk"] is None
    assert not result.report["schema_transformation"]
    assert len(result.report["conversions"]) == 1
    assert not any(s["stage"] == "transformation" for s in result.report["steps"])


def test_same_schema_same_format(service, metadata):
    result = service.transform(
        TransformationRequest(metadata, "datacite-4.1", "datacite-4.1")
    )
    assert result.metadata == metadata
    assert result.report["crosswalk"] is None
    assert result.report["conversions"] == []


def test_missing_converter_does_not_fall_back(service, metadata):
    service.catalog.converters = [
        c for c in service.catalog.converters if c.schema != "oai-dc"
    ]
    with pytest.raises(TransformationError) as err:
        service.transform(
            TransformationRequest(
                metadata, "datacite-4.1", "oai-dc", output_format="json"
            )
        )
    assert err.value.code == "no_converter"
    assert not any(s["stage"] == "transformation" for s in err.value.steps)


def test_ambiguous_mapping_independent_of_format(service, metadata):
    service.catalog.crosswalks.append(
        replace(service.catalog.crosswalks[0], id="alternative")
    )
    with pytest.raises(TransformationError) as err:
        service.transform(TransformationRequest(metadata, "datacite-4.1", "oai-dc"))
    assert err.value.code == "ambiguous_crosswalk"


def test_native_output_validated_before_conversion(service):
    dc = (
        (ROOT / "examples/inputs/dublincore.xml")
        .read_text()
        .replace("<dc:creator>Wijngaarden, Marcella</dc:creator>", "")
    )
    with pytest.raises(TransformationError) as err:
        service.transform(
            TransformationRequest(dc, "oai-dc", "datacite-4.1", output_format="json")
        )
    assert err.value.stage == "native_target_validation"
    assert not any(s["stage"] == "output_conversion" for s in err.value.steps)


def test_dc_language_field_is_preserved_by_conversion(service):
    req = TransformationRequest(
        json.dumps({"title": ["One", "Two"], "language": "nl"}),
        "oai-dc",
        "oai-dc",
        input_format="json",
        output_format="xml",
    )
    xml = service.transform(req).metadata
    back = service.transform(
        TransformationRequest(xml, "oai-dc", "oai-dc", output_format="json")
    )
    assert json.loads(back.metadata) == {"title": ["One", "Two"], "language": "nl"}


def test_discovery_separates_operations(client):
    assert len(client.get("/api/v1/crosswalks").json["crosswalks"]) == 2
    assert len(client.get("/api/v1/converters").json["converters"]) == 4
