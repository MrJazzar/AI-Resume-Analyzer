from app.rag.document_loader import Document


class DocumentChunk:
    def __init__(
        self,
        content: str,
        source: str,
        chunk_index: int,
    ):
        self.content = content
        self.source = source
        self.chunk_index = chunk_index


class DocumentChunker:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(
        self,
        documents: list[Document],
    ) -> list[DocumentChunk]:

        chunks = []

        for document in documents:
            text = document.content

            start = 0
            chunk_index = 0

            while start < len(text):
                end = start + self.chunk_size

                chunk_text = text[start:end].strip()

                if chunk_text:
                    chunks.append(
                        DocumentChunk(
                            content=chunk_text,
                            source=document.source,
                            chunk_index=chunk_index,
                        )
                    )

                start = end - self.chunk_overlap
                chunk_index += 1

        return chunks