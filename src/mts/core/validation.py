"""Schema validation coordinated without format-specific branching."""

from .exceptions import TransformationError
from .formats import default_formats


class Validator:
    """Compile catalog schemas with the registered format implementations."""

    def __init__(self, catalog, formats=None):
        self.formats = default_formats() if formats is None else dict(formats)
        self.validators = {}
        for schema_id, schema in catalog.schemas.items():
            for fmt, filename in schema["formats"].items():
                if fmt not in self.formats:
                    raise ValueError(f"Unregistered catalog format: {fmt}")
                path = catalog.local_path(filename)
                self.validators[schema_id, fmt] = self.formats[fmt].compile_schema(path)

    def validate(self, content, schema_id, fmt, stage):
        """Attach workflow context to content validation failures."""
        try:
            self.validators[schema_id, fmt](content)
        except (ValueError, TransformationError) as exc:
            raise TransformationError(
                "validation_failed", str(exc), stage=stage
            ) from exc
