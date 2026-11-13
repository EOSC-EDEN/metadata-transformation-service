"""Shared fixtures use explicit paths, independent of the working directory."""

from pathlib import Path

import pytest

from mts.api import create_app
from mts.config import Config
from mts.core.transformation import TransformationService

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config():
    return Config(resource_path=ROOT / "resources")


@pytest.fixture
def service(config):
    return TransformationService(config)


@pytest.fixture
def client(config):
    return create_app(config).test_client()


@pytest.fixture
def metadata():
    return (ROOT / "examples/inputs/datacite.xml").read_text()
