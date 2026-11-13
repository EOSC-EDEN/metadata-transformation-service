"""Run all bundled examples from the project root: python examples/transform.py."""

import json
from pathlib import Path

from mts.config import Config
from mts.core.models import TransformationRequest
from mts.core.transformation import TransformationService

service = TransformationService(Config())
for source, target, filename, output_format, output_name in [
    ("datacite-4.1", "oai-dc", "datacite.xml", "xml", "dublincore.xml"),
    ("oai-dc", "datacite-4.1", "dublincore.xml", "xml", "datacite.xml"),
    ("datacite-4.1", "datacite-4.1", "datacite.xml", "json", "datacite.json"),
]:
    result = service.transform(
        TransformationRequest(
            metadata=Path("examples/inputs", filename).read_text(),
            source_schema=source,
            target_schema=target,
            output_format=output_format,
        )
    )
    Path("examples/outputs").mkdir(exist_ok=True)
    Path("examples/outputs", output_name).write_text(result.metadata)
    print(output_name, result.report)

# Additional cross-schema examples for XML and JSON in either direction.

for case in json.loads(Path("examples/combinations.json").read_text()):
    result = service.transform(
        TransformationRequest(
            metadata=Path("examples/inputs", case["input"]).read_text(),
            source_schema=case["source"],
            target_schema=case["target"],
            input_format=case["input_format"],
            output_format=case["output_format"],
        )
    )
    Path("examples/outputs", case["output"]).write_text(result.metadata)
    print(case["output"], result.report["status"])

# Direct same-schema conversions do not select a crosswalk.
for schema, stem, input_format, output_format in [
    ("datacite-4.1", "datacite", "json", "xml"),
    ("oai-dc", "dublincore", "xml", "json"),
    ("oai-dc", "dublincore", "json", "xml"),
]:
    result = service.transform(
        TransformationRequest(
            metadata=Path("examples/inputs", f"{stem}.{input_format}").read_text(),
            source_schema=schema,
            target_schema=schema,
            input_format=input_format,
            output_format=output_format,
        )
    )
    name = f"{stem}-converted.{output_format}"
    Path("examples/outputs", name).write_text(result.metadata)
    print(name, result.report)
