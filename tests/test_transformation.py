"""Behavioral coverage for valid transformations and meaningful failure paths."""

import json
from dataclasses import replace

import pytest
from conftest import ROOT
from lxml import etree

from mts.core.exceptions import TransformationError
from mts.core.models import TransformationRequest
from mts.core.transformation import TransformationService


@pytest.mark.parametrize(
    "source,target,filename,fmt,expected",
    [
        ("datacite-4.1", "oai-dc", "datacite.xml", "xml", "dublincore.xml"),
        ("oai-dc", "datacite-4.1", "dublincore.xml", "xml", "datacite.xml"),
        ("datacite-4.1", "datacite-4.1", "datacite.xml", "json", "datacite.json"),
    ],
)
def test_examples(service, source, target, filename, fmt, expected):
    result = service.transform(
        TransformationRequest(
            (ROOT / "examples/inputs" / filename).read_text(),
            source,
            target,
            output_format=fmt,
        )
    )
    wanted = (ROOT / "examples/outputs" / expected).read_text()
    if fmt == "json":
        assert json.loads(result.metadata) == json.loads(wanted)
    else:
        # Prefixes and indentation are not metadata differences.
        def signature(text):
            root = etree.fromstring(text.encode())
            return [
                (e.tag, dict(e.attrib), (e.text or "").strip()) for e in root.iter()
            ]

        assert signature(result.metadata) == signature(wanted)
    assert result.report["steps"][-1] == {
        "stage": "target_validation",
        "status": "passed",
    }
    assert result.report["serialization_transformation"] == (fmt == "json")


@pytest.mark.parametrize(
    "content",
    [
        "<broken>",
        "<other/>",
        '<!DOCTYPE resource [<!ENTITY x "test">]><resource>&x;</resource>',
    ],
)
def test_invalid_source(service, content):
    with pytest.raises(TransformationError) as exc:
        service.transform(TransformationRequest(content, "datacite-4.1", "oai-dc"))
    assert exc.value.stage == "source_validation"


@pytest.mark.parametrize(
    "changes,code",
    [
        ({"target_schema": "unknown"}, "unknown_schema"),
        ({"output_format": "csv"}, "unsupported_format"),
        ({"crosswalk_id": "missing"}, "no_crosswalk"),
    ],
)
def test_selection_errors(service, metadata, changes, code):
    req = replace(TransformationRequest(metadata, "datacite-4.1", "oai-dc"), **changes)
    with pytest.raises(TransformationError) as exc:
        service.transform(req)
    assert exc.value.code == code


def test_ambiguous_selection(service, metadata):
    service.catalog.crosswalks.append(
        replace(service.catalog.crosswalks[0], id="alternative")
    )
    req = TransformationRequest(metadata, "datacite-4.1", "oai-dc")
    with pytest.raises(TransformationError, match="Specify"):
        service.transform(req)
    assert service.transform(replace(req, crosswalk_id="datacite-to-dc"))


def test_missing_target_information(service):
    dc = (ROOT / "examples/inputs/dublincore.xml").read_text()
    dc = dc.replace("<dc:creator>Wijngaarden, Marcella</dc:creator>", "")
    with pytest.raises(TransformationError) as exc:
        service.transform(TransformationRequest(dc, "oai-dc", "datacite-4.1"))
    assert exc.value.stage == "target_validation"
    assert exc.value.steps[-1]["status"] == "failed"


def test_size_limit(config, metadata):
    service = TransformationService(replace(config, max_metadata_bytes=10))
    with pytest.raises(TransformationError) as exc:
        service.transform(TransformationRequest(metadata, "datacite-4.1", "oai-dc"))
    assert exc.value.code == "metadata_too_large"


def test_json_converter_rejects_unsupported_fields(service, metadata):
    metadata = metadata.replace("</resource>", "<language>en</language></resource>")
    with pytest.raises(TransformationError) as exc:
        service.transform(
            TransformationRequest(
                metadata, "datacite-4.1", "datacite-4.1", output_format="json"
            )
        )
    assert exc.value.stage == "output_conversion"


def test_json_validation(service):
    with pytest.raises(TransformationError) as exc:
        service.validator.validate("{}", "datacite-4.1", "json", "target_validation")
    assert exc.value.stage == "target_validation"


def test_repeat_values_preserved(service, metadata):
    metadata = metadata.replace("</titles>", "<title>Second title</title></titles>")
    output = service.transform(
        TransformationRequest(
            metadata, "datacite-4.1", "datacite-4.1", output_format="json"
        )
    )
    assert len(json.loads(output.metadata)["titles"]) == 2


def test_json_serializer_escapes_values(service, metadata):
    metadata = metadata.replace(
        "Example research dataset", "A &quot;quoted&quot; title &amp; café"
    )
    result = service.transform(
        TransformationRequest(
            metadata, "datacite-4.1", "datacite-4.1", output_format="json"
        )
    )
    assert (
        json.loads(result.metadata)["titles"][0]["title"] == 'A "quoted" title & café'
    )
