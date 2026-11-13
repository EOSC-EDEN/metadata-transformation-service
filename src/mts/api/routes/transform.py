"""Normalize JSON text submissions and multipart uploads into core requests."""

from dataclasses import asdict, fields

from flask import Blueprint, request

from mts.core.exceptions import TransformationError
from mts.core.models import TransformationRequest


def create_transform_blueprint(service):
    """Both transport methods execute exactly the same core workflow."""
    blueprint = Blueprint("transform", __name__, url_prefix="/api/v1")

    @blueprint.post("/transform")
    def transform():
        if request.mimetype == "multipart/form-data":
            data = request.form.to_dict()
            if "file" not in request.files or "metadata" in data:
                raise TransformationError(
                    "invalid_request", "Supply exactly one metadata file"
                )
            raw = request.files["file"].read(service.config.max_metadata_bytes + 1)
            if len(raw) > service.config.max_metadata_bytes:
                raise TransformationError(
                    "metadata_too_large", "Metadata exceeds configured limit"
                )
            try:
                data["metadata"] = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise TransformationError(
                    "invalid_request", "Use UTF-8 metadata"
                ) from exc
        elif request.is_json:
            data = request.get_json()
        else:
            raise TransformationError(
                "unsupported_media_type", "Use JSON or multipart/form-data"
            )
        allowed = {f.name for f in fields(TransformationRequest)}
        if not isinstance(data, dict) or set(data) - allowed:
            raise TransformationError(
                "invalid_request", "Expected an object with supported fields"
            )
        required = {"metadata", "source_schema", "target_schema"}
        if not required <= data.keys() or any(
            not isinstance(v, str) or not v.strip() for v in data.values()
        ):
            raise TransformationError(
                "invalid_request", "Fields must be nonempty strings"
            )
        return asdict(service.transform(TransformationRequest(**data)))

    return blueprint
