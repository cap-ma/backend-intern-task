
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_reingest_replaces_document(client):
    client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "cats", "text": "Cats are lovely pets."}
            ]
        }
    )

    client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "cats", "text": "Dogs are loyal animals."}
            ]
        }
    )

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == {
        "documents": [{"id": "cats", "chunks": 1}]
    }

    response = client.post(
        "/ask",
        json={"question": "What are dogs?"}
    )

    assert response.status_code == 200
    assert response.json()["sources"][0]["text"] == "Dogs are loyal animals."


def test_ingest_empty_documents(client):
    response = client.post(
        "/ingest",
        json={"documents": []}
    )

    assert response.status_code == 422


def test_ingest_empty_id(client):
    response = client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "   ", "text": "Cats are lovely pets."}
            ]
        }
    )

    assert response.status_code == 422


def test_ingest_empty_text(client):
    response = client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "cats", "text": "   "}
            ]
        }
    )

    assert response.status_code == 422

def test_ingest_duplicate_document_ids(client):
    response = client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "cats", "text": "Cats are lovely pets."},
                {"id": "cats", "text": "Cats are independent animals."}
            ]
        }
    )

    assert response.status_code == 422


def test_ingest_validation_error_does_not_modify_store(client):
    client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "cats", "text": "Old cats document."}
            ]
        }
    )

    response = client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "dogs", "text": "Valid document."},
                {"id": "birds", "text": "   "}
            ]
        }
    )

    assert response.status_code == 422

    response = client.get("/documents")

    assert response.json() == {
        "documents": [
            {"id": "cats", "chunks": 1}
        ]
    }