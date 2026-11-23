def chunk_text(text: str, size: int = 50, overlap: int = 10) -> list[str]:
    if size <= 0:
        raise ValueError("size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= size:
        raise ValueError("overlap must be less than size")

    words = text.split()

    if not words:
        return []

    step = size - overlap
    chunks = []

    for i in range(0, len(words), step):
        chunk_words = words[i:i + size]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)

        if i + size >= len(words):
            break

    return chunks
