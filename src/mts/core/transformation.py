"""Validate, optionally convert, map schemas, and convert to the requested output."""

from .catalog import Catalog
from .engines.xslt import XsltEngine
from .exceptions import TransformationError
from .formats import default_formats
from .models import TransformationResult
from .validation import Validator


class TransformationService:
    """One schema crosswalk, with at most one conversion on either side."""

    def __init__(self, config, *, formats=None, engines=None):
        self.config = config
        self.catalog = Catalog(config.resource_path)
        self.formats = default_formats() if formats is None else dict(formats)
        self.validator = Validator(self.catalog, self.formats)
        self.engines = [XsltEngine()] if engines is None else list(engines)
        self.operation_engines = {}
        for operation in self.catalog.crosswalks + self.catalog.converters:
            matches = [
                engine for engine in self.engines if engine.accepts(operation.path)
            ]
            if len(matches) != 1:
                raise ValueError(f"Cannot infer engine for {operation.id}")
            if operation.input_format not in matches[0].input_formats:
                raise ValueError(
                    f"Engine cannot read {operation.input_format} for {operation.id}"
                )
            self.operation_engines[operation.id] = matches[0]

    @staticmethod
    def _identity(operation):
        """Public provenance without exposing server filesystem paths."""
        return {
            "id": operation.id,
            "version": operation.version,
            "source": "local",
            "notes": list(operation.notes),
        }

    def _execute(self, operation, content, stage, steps, warnings):
        """Execute either kind of resource and attach the actual failing stage."""
        try:
            output, messages = self.operation_engines[operation.id].transform(
                content, operation
            )
        except TransformationError as exc:
            exc.stage = stage
            raise
        warnings.extend(messages)
        steps.append({"stage": stage, "status": "passed", "operation_id": operation.id})
        return output

    def transform(self, request):
        """Return validated output using an independently selected schema mapping."""
        steps, warnings, conversions = [], [], []
        crosswalk = None
        try:
            if not isinstance(request.metadata, str) or not request.metadata.strip():
                raise TransformationError(
                    "invalid_request", "metadata must be nonempty text"
                )
            if len(request.metadata.encode("utf-8")) > self.config.max_metadata_bytes:
                raise TransformationError(
                    "metadata_too_large", "Metadata exceeds configured limit"
                )
            self.catalog.validate_request(request)
            self.validator.validate(
                request.metadata,
                request.source_schema,
                request.input_format,
                "source_validation",
            )
            steps.append({"stage": "source_validation", "status": "passed"})

            # Resolve both optional conversions before executing anything.
            if request.source_schema != request.target_schema or request.crosswalk_id:
                crosswalk = self.catalog.select(request)
                before = self.catalog.converter(
                    request.source_schema, request.input_format, crosswalk.input_format
                )
                after = self.catalog.converter(
                    request.target_schema,
                    crosswalk.output_format,
                    request.output_format,
                )
                steps.append(
                    {
                        "stage": "crosswalk_selection",
                        "status": "passed",
                        "crosswalk_id": crosswalk.id,
                    }
                )
            else:
                # Same schema: direct conversion, or a validated pass-through.
                before = None
                after = self.catalog.converter(
                    request.source_schema, request.input_format, request.output_format
                )

            output = request.metadata
            if before:
                output = self._execute(
                    before, output, "input_conversion", steps, warnings
                )
                conversions.append(
                    {**self._identity(before), "stage": "input_conversion"}
                )
                self.validator.validate(
                    output,
                    before.schema,
                    before.output_format,
                    "input_conversion_validation",
                )
                steps.append(
                    {"stage": "input_conversion_validation", "status": "passed"}
                )
            if crosswalk:
                output = self._execute(
                    crosswalk, output, "transformation", steps, warnings
                )
                # Validate the native output before a converter can hide an error.
                if after:
                    self.validator.validate(
                        output,
                        request.target_schema,
                        crosswalk.output_format,
                        "native_target_validation",
                    )
                    steps.append(
                        {"stage": "native_target_validation", "status": "passed"}
                    )
            if after:
                output = self._execute(
                    after, output, "output_conversion", steps, warnings
                )
                conversions.append(
                    {**self._identity(after), "stage": "output_conversion"}
                )
            self.validator.validate(
                output,
                request.target_schema,
                request.output_format,
                "target_validation",
            )
            steps.append({"stage": "target_validation", "status": "passed"})
        except TransformationError as exc:
            exc.steps = steps + [{"stage": exc.stage, "status": "failed"}]
            raise
        return TransformationResult(
            metadata=output,
            media_type=self.formats[request.output_format].media_type,
            report={
                "status": "success_with_warnings" if warnings else "success",
                "crosswalk": self._identity(crosswalk) if crosswalk else None,
                "conversions": conversions,
                "schema_transformation": request.source_schema != request.target_schema,
                "serialization_transformation": bool(conversions),
                "steps": steps,
                "warnings": warnings,
            },
        )
