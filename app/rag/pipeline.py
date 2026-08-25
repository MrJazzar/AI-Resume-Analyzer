from app.rag.document_loader import DocumentLoader
from app.rag.chunker import DocumentChunker
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore
from app.rag.retriever import Retriever
from app.rag.generator import RAGGenerator


class RAGPipeline:

    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

        self.retriever = Retriever(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
        )

        self.generator = RAGGenerator()

    def index_knowledge_base(self):
        documents = self.loader.load_documents()

        chunks = self.chunker.chunk_documents(documents)

        embeddings = self.embedding_service.embed_documents(
            [chunk.content for chunk in chunks]
        )

        self.vector_store.add_documents(
            documents=chunks,
            embeddings=embeddings,
        )

        return {
            "documents": len(documents),
            "chunks": len(chunks),
        }

    def retrieve(self, query: str, top_k: int = 5):
        return self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )

    def ask(self, question: str, top_k: int = 5):
        if self.vector_store.count() == 0:
            self.index_knowledge_base()

        results = self.retrieve(
            query=question,
            top_k=top_k,
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        context_documents = []

        for content, metadata in zip(documents, metadatas):
            context_documents.append(
                {
                    "content": content,
                    "source": metadata["source"],
                }
            )

        return self.generator.generate(
            question=question,
            context_documents=context_documents,
        )