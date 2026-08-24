from app.rag.pipeline import RAGPipeline


def test_retrieval():
    pipeline = RAGPipeline()

    result = pipeline.index_knowledge_base()

    assert result["documents"] > 0
    assert result["chunks"] > 0

    results = pipeline.retrieve(
        "What Python skills are useful for AI Engineering?",
        top_k=3,
    )

    assert results["documents"]
    assert results["metadatas"]