from app.rag.embeddings import EmbeddingService


def test_embedding():
    service = EmbeddingService()

    embedding = service.embed_query(
        "What Python skills do I need?"
    )

    assert len(embedding) > 0
    assert isinstance(embedding[0], float)