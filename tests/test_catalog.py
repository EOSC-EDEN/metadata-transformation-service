"""Catalog boundary checks and stylesheet language inference."""

import pytest

from mts.core.engines.xslt import XsltEngine


def test_path_escape(service):
    with pytest.raises(ValueError):
        service.catalog.local_path("../README.md")


def test_language_inference_ignores_extension(tmp_path):
    path = tmp_path / "mapping.txt"
    path.write_text(
        '<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"'
        ' version="3.0"/>'
    )
    assert XsltEngine().accepts(path)
    path.write_text("<unrelated/>")
    assert not XsltEngine().accepts(path)
