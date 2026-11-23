import pytest
def test_ask_empty_question(client):
    client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "cats", "text": "Cats are lovely pets."}
            ]
        }
    )

    response = client.post(
        "/ask",
        json={"question": "   "}
    )

    assert response.status_code == 422


@pytest.mark.parametrize("top_k", [0, 11, -1])
def test_ask_invalid_top_k(client, top_k):
    client.post(
        "/ingest",
        json={
            "documents": [
                {"id": "cats", "text": "Cats are lovely pets."}
            ]
        }
    )

    response = client.post(
        "/ask",
        json={
            "question": "What are cats?",
            "top_k": top_k
        }
    )

    assert response.status_code == 422


def test_ask_without_documents(client):
    response = client.post(
        "/ask",
        json={"question": "What are cats?"}
    )

    assert response.status_code == 404