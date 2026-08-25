import json
import httpx

from app.config import settings


class RAGGenerator:
    def generate(
        self,
        question: str,
        context_documents: list[dict],
    ) -> dict:

        context_parts = []

        for document in context_documents:
            context_parts.append(
                f"Source: {document['source']}\n"
                f"Content:\n{document['content']}"
            )

        context = "\n\n---\n\n".join(context_parts)

        prompt = f"""
You are a career advisor.

Answer the user's question using ONLY the provided context.

If the context does not contain enough information to answer the question,
say that the available knowledge base does not contain enough information.

Do not invent facts.

User Question:
{question}

Retrieved Context:
{context}

Return valid JSON. Always include "answer" and "sources". If the user
question requests additional structured fields, include those fields in the
same JSON response and fill them using the provided context. Use this base
structure:
{{
    "answer": "your answer",
    "sources": ["source1", "source2"]
}}
"""

        if not settings.AI_API_KEY:
            raise RuntimeError("AI_API_KEY is not configured")

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{settings.AI_MODEL}:generateContent"
        )

        response = httpx.post(
            url,
            params={"key": settings.AI_API_KEY},
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt,
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0,
                    "responseMimeType": "application/json",
                },
            },
            timeout=60,
        )

        response.raise_for_status()

        result_text = (
            response.json()["candidates"][0]["content"]["parts"][0]["text"]
        )

        return json.loads(result_text)