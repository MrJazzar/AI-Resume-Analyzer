from pathlib import Path


class Document:
    def __init__(self, content: str, source: str):
        self.content = content
        self.source = source


class DocumentLoader:
    def __init__(self, knowledge_base_path: str = "knowledge_base"):
        self.knowledge_base_path = Path(knowledge_base_path)

    def load_documents(self) -> list[Document]:
        documents = []

        for file_path in self.knowledge_base_path.rglob("*.md"):
            content = file_path.read_text(encoding="utf-8").strip()

            if not content:
                continue

            documents.append(
                Document(
                    content=content,
                    source=str(file_path),
                )
            )

        return documents