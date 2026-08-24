from app.rag.document_loader import DocumentLoader


def test_load_documents():
    loader = DocumentLoader()

    documents = loader.load_documents()

    assert len(documents) > 0

    for document in documents:
        assert document.content
        assert document.source.endswith(".md")