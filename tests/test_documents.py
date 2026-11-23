from fastapi.testclient import TestClient
from app.main import create_app


def test_get_documents(client):
    client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "cats", "text": "Cats are lovely pets."}
            ]
        }
    )

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == {
        "documents": [
            {"id": "cats", "chunks": 1}
        ]
    }


def test_delete_document(client):
    client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "cats", "text": "Cats are lovely pets."}
            ]
        }
    )

    response = client.delete("/documents/cats")

    assert response.status_code == 204

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == {"documents": []}


def test_create_app_has_separate_store():
    client1 = TestClient(create_app())
    client2 = TestClient(create_app())

    client1.post(
        "/ingest",
        json={
            "documents": [
                {"id": "cats", "text": "Cats are lovely pets."}
            ]
        }
    )

    response = client2.get("/documents")

    assert response.status_code == 200
    assert response.json() == {"documents": []}


def test_delete_nonexistent_document(client):
    response = client.delete("/documents/unknown")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found"
    }