"""Validate the API document as part of the ordinary test suite."""

import yaml
from conftest import ROOT
from openapi_spec_validator import validate


def test_openapi_is_valid():
    validate(yaml.safe_load((ROOT / "docs/openapi.yaml").read_text()))
