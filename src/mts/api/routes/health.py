"""Health check endpoint."""

from flask import Blueprint

health = Blueprint("health", __name__)


@health.get("/health")
def check_health():
    """The app only starts after catalog and validators load successfully."""
    return {"status": "ok"}
