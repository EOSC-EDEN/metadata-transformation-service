"""The API contract covers text, uploads, discovery, and transport failures."""

import io
from dataclasses import replace

import pytest

from mts.api import create_app


@pytest.mark.parametrize(
    "path", ["/health", "/api/v1/schemas", "/api/v1/crosswalks", "/api/v1/capabilities"]
)
def test_discovery(client, path):
    assert client.get(path).status_code == 200


def test_text_and_upload_agree(client, metadata):
    fields = {"source_schema": "datacite-4.1", "target_schema": "oai-dc"}
    text = client.post("/api/v1/transform", json={**fields, "metadata": metadata})
    upload = client.post(
        "/api/v1/transform",
        data={**fields, "file": (io.BytesIO(metadata.encode()), "record.xml")},
    )
    assert text.status_code == upload.status_code == 200
    assert text.json == upload.json


@pytest.mark.parametrize("body", [None, [], {}, {"metadata": 42}, {"unknown": "value"}])
def test_invalid_fields(client, body):
    response = client.post("/api/v1/transform", json=body)
    assert response.status_code in (400, 415)
    assert "error" in response.json


def test_invalid_xml(client):
    response = client.post(
        "/api/v1/transform",
        json={
            "metadata": "<bad>",
            "source_schema": "datacite-4.1",
            "target_schema": "oai-dc",
        },
    )
    assert response.status_code == 422
    assert "metadata" not in response.json


def test_transport_limit(config):
    client = create_app(replace(config, max_request_bytes=100)).test_client()
    response = client.post(
        "/api/v1/transform", data="x" * 101, content_type="application/json"
    )
    assert response.status_code == 413
    assert response.is_json


def test_invalid_utf8(client):
    response = client.post(
        "/api/v1/transform", data={"file": (io.BytesIO(b"\xff"), "record.xml")}
    )
    assert response.status_code == 400


def test_malformed_json(client):
    response = client.post(
        "/api/v1/transform", data="{", content_type="application/json"
    )
    assert response.status_code == 400
    assert response.is_json
