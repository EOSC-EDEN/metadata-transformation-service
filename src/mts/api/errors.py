"""Consistent machine-readable errors, including Flask transport failures."""

from werkzeug.exceptions import HTTPException

from mts.core.exceptions import TransformationError


def register_error_handlers(app):
    """Map domain failures to appropriate HTTP statuses."""

    @app.errorhandler(TransformationError)
    def domain_error(exc):
        status = {
            "metadata_too_large": 413,
            "unsupported_media_type": 415,
            "validation_failed": 422,
            "execution_failed": 422,
        }.get(exc.code, 400)
        return {
            "error": {"code": exc.code, "message": str(exc), "stage": exc.stage},
            "report": {"status": "failed", "steps": exc.steps},
        }, status

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return {
            "error": {"code": str(exc.code), "message": exc.description},
            "report": {"status": "failed", "steps": []},
        }, exc.code

    @app.errorhandler(Exception)
    def unexpected_error(exc):
        app.logger.exception("Unexpected transformation service failure")
        return {
            "error": {"code": "internal_error", "message": "Internal service error"},
            "report": {"status": "failed", "steps": []},
        }, 500
