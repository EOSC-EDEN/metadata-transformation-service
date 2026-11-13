"""Flask application factory: construct dependencies and register routes."""

from flask import Flask

from mts.config import Config
from mts.core.transformation import TransformationService

from .errors import register_error_handlers
from .routes.catalog import catalog_blueprint
from .routes.health import health
from .routes.transform import create_transform_blueprint


def create_app(config: Config | None = None, *, formats=None, engines=None):
    """Create an independent app and service, also suitable for pytest fixtures."""
    config = config or Config.from_env()
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = config.max_request_bytes
    service = TransformationService(config, formats=formats, engines=engines)
    app.register_blueprint(health)
    app.register_blueprint(catalog_blueprint(service))
    app.register_blueprint(create_transform_blueprint(service))
    register_error_handlers(app)
    return app
