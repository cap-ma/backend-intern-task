import pytest
from app.chunking import chunk_text
def test_chunk_text_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


@pytest.mark.parametrize(
    "size, overlap",
    [
        (0, 0),
        (-1, 0),
        (5, -1),
        (5, 5),
        (5, 6),
    ]
)
def test_chunk_text_invalid_parameters(size, overlap):
    with pytest.raises(ValueError):
        chunk_text("Python Django FastAPI", size, overlap)


def test_chunk_text_respects_size():
    text = "one two three four five six seven eight"

    chunks = chunk_text(text, size=3, overlap=1)

    for chunk in chunks:
        assert len(chunk.split()) <= 3
