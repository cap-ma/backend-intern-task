
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app import llm
from app.chunking import chunk_text


# Request models
class Document(BaseModel):
    id: str
    text: str


class IngestRequest(BaseModel):
    documents: list[Document]


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=3, ge=1, le=10)


def create_app() -> FastAPI:
    app = FastAPI()

    # In-memory storage
    store = {}

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Ingest documents
    @app.post("/ingest")
    def ingest(request: IngestRequest):
        if not request.documents:
            raise HTTPException(
                status_code=422,
                detail="Documents cannot be empty"
            )

        # 1. Validation
        prepared_docs: list[tuple[str, str]] = []
        seen_ids = set()

        for document in request.documents:
            doc_id = document.id.strip()
            text = document.text.strip()

            if not doc_id or not text:
                raise HTTPException(
                    status_code=422,
                    detail="Document id and text cannot be empty"
                )

            if doc_id in seen_ids:
                raise HTTPException(
                    status_code=422,
                    detail=f"Duplicate document id: {doc_id}"
                )

            seen_ids.add(doc_id)
            prepared_docs.append((doc_id, text))

        # 2. Preparation
        prepared_records: dict[str, list[dict]] = {}
        total_chunks = 0

        for doc_id, text in prepared_docs:
            text_chunks = chunk_text(text)
            doc_records = []

            for index, chunk in enumerate(text_chunks):
                chunk_id = f"{doc_id}:{index}"
                embedding = llm.embed(chunk)

                doc_records.append({
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "text": chunk,
                    "embedding": embedding,
                })

            prepared_records[doc_id] = doc_records
            total_chunks += len(doc_records)

        # 3. Commit
        for doc_id, doc_records in prepared_records.items():
            old_chunk_ids = [
                chunk_id
                for chunk_id, item in store.items()
                if item["doc_id"] == doc_id
            ]

            for chunk_id in old_chunk_ids:
                del store[chunk_id]

            for record in doc_records:
                store[record["chunk_id"]] = record

        return {
            "ingested": len(prepared_docs),
            "chunks": total_chunks,
        }

    # Ask a question
    @app.post("/ask")
    def ask(request: AskRequest):
        question = request.question.strip()

        if not question:
            raise HTTPException(
                status_code=422,
                detail="Question cannot be empty"
            )

        if not store:
            raise HTTPException(
                status_code=404,
                detail="No documents ingested"
            )

        question_embedding = llm.embed(question)

        scored_chunks = []

        for chunk in store.values():
            chunk_embedding = chunk["embedding"]

            # Cosine similarity (unit vectors)
            score = sum(
                a * b
                for a, b in zip(question_embedding, chunk_embedding)
            )

            scored_chunks.append({
                "doc_id": chunk["doc_id"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "score": score,
            })

        # Highest similarity first
        scored_chunks.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        best_chunks = scored_chunks[:request.top_k]

        contexts = [
            chunk["text"]
            for chunk in best_chunks
        ]

        answer = llm.generate(question, contexts)

        sources = [
            {
                "doc_id": chunk["doc_id"],
                "chunk_id": chunk["chunk_id"],
                "score": chunk["score"],
                "text": chunk["text"],
            }
            for chunk in best_chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }

    # List documents
    @app.get("/documents")
    def get_documents():
        documents = {}

        for chunk in store.values():
            doc_id = chunk["doc_id"]

            if doc_id not in documents:
                documents[doc_id] = 0

            documents[doc_id] += 1

        return {
            "documents": [
                {"id": doc_id, "chunks": count}
                for doc_id, count in sorted(documents.items())
            ]
        }

    # Delete document
    @app.delete("/documents/{doc_id}", status_code=204)
    def delete_document(doc_id: str):
        chunk_ids = [
            chunk_id
            for chunk_id, chunk in store.items()
            if chunk["doc_id"] == doc_id
        ]

        if not chunk_ids:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        for chunk_id in chunk_ids:
            del store[chunk_id]

        return None

    return app


app = create_app()
