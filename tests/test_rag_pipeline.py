import pytest

from app.config import settings
from app.rag.pipeline import RAGPipeline


@pytest.mark.skipif(
    not settings.AI_API_KEY,
    reason="AI_API_KEY is not configured",
)
def test_rag_pipeline():
    pipeline = RAGPipeline()

    pipeline.index_knowledge_base()

    result = pipeline.ask(
        "What Python skills are useful for an AI Engineer?"
    )

    assert result["answer"]
    assert isinstance(result["sources"], list)