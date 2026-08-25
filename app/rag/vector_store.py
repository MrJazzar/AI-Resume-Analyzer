from pathlib import Path

import chromadb


class VectorStore:
    def __init__(
        self,
        persist_directory: str = "data/chroma",
        collection_name: str = "career_knowledge",
    ):
        Path(persist_directory).mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = chromadb.PersistentClient(
            path=persist_directory,
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
        )

    def add_documents(
        self,
        documents,
        embeddings: list[list[float]],
    ):
        ids = [
            f"{document.source}_{document.chunk_index}"
            for document in documents
        ]

        self.collection.upsert(
            ids=ids,
            documents=[document.content for document in documents],
            embeddings=embeddings,
            metadatas=[
                {
                    "source": document.source,
                    "chunk_index": document.chunk_index,
                }
                for document in documents
            ],
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

    def count(self) -> int:
        return self.collection.count()