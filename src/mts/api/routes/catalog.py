"""Publish the capabilities of this particular deployment."""

from dataclasses import asdict

from flask import Blueprint


def catalog_blueprint(service):
    """Bind a service explicitly, without a global application proxy."""
    blueprint = Blueprint("catalog", __name__, url_prefix="/api/v1")

    @blueprint.get("/schemas")
    def schemas():
        return {
            "schemas": [
                {"id": s["id"], "version": s["version"], "formats": list(s["formats"])}
                for s in service.catalog.schemas.values()
            ]
        }

    @blueprint.get("/crosswalks")
    def crosswalks():
        items = []
        for crosswalk in service.catalog.crosswalks:
            item = asdict(crosswalk)
            del item["path"]
            item.update(service.catalog.supported_formats(crosswalk))
            items.append(item)
        return {"crosswalks": items}

    @blueprint.get("/converters")
    def converters():
        """List direct serialization conversions independently of crosswalks."""
        return {
            "converters": [
                {k: v for k, v in asdict(c).items() if k != "path"}
                for c in service.catalog.converters
            ]
        }

    @blueprint.get("/capabilities")
    def capabilities():
        return {
            "max_metadata_bytes": service.config.max_metadata_bytes,
            "max_request_bytes": service.config.max_request_bytes,
            "input_formats": sorted(
                {
                    fmt
                    for schema in service.catalog.schemas.values()
                    for fmt in schema["formats"]
                }
            ),
            "output_formats": sorted(
                {
                    fmt
                    for schema in service.catalog.schemas.values()
                    for fmt in schema["formats"]
                }
            ),
            "media_types": {
                name: fmt.media_type for name, fmt in service.formats.items()
            },
        }

    return blueprint
