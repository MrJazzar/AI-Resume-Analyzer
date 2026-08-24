from app.rag.document_loader import DocumentLoader
from app.rag.chunker import DocumentChunker


def test_chunk_documents():
    loader = DocumentLoader()
    documents = loader.load_documents()

    chunker = DocumentChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk_documents(documents)

    assert len(chunks) > 0

    for chunk in chunks:
        assert chunk.content
        assert chunk.source
        assert chunk.chunk_index >= 0