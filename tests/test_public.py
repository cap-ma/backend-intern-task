"""A few public tests to get you started.

The grader runs a larger hidden test suite against the same spec in README.md.
Passing these tests does NOT mean you will pass the hidden ones.
"""

import pytest
from fastapi.testclient import TestClient

from app.chunking import chunk_text

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_chunk_text_basic():
    text = " ".join(f"w{i}" for i in range(12))
    assert chunk_text(text, size=5, overlap=2) == [
        "w0 w1 w2 w3 w4",
        "w3 w4 w5 w6 w7",
        "w6 w7 w8 w9 w10",
        "w9 w10 w11",
    ]


def test_ingest_then_ask(client):
    r = client.post(
        "/ingest",
        json={"documents": [{"id": "cats", "text": "Cats are small furry pets that purr."}]},
    )
    assert r.status_code == 200
    assert r.json() == {"ingested": 1, "chunks": 1}

    r = client.post("/ask", json={"question": "Which pets purr?"})
    assert r.status_code == 200
    body = r.json()
    assert body["sources"][0]["doc_id"] == "cats"
    assert body["sources"][0]["chunk_id"] == "cats:0"






