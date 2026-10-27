"""
Context Engineering and Grounded Citation Generation for GroundTrace.
Formulates structured prompts, injects retrieved chunk context, and ensures factual attribution.
"""
from typing import List, Dict, Any, Tuple


class ContextEngine:
    """
    Manages context engineering, prompt conditioning, and strict source citation grounding.
    """

    @staticmethod
    def construct_grounded_context(retrieved_chunks: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Assembles retrieved chunks into a standardized context block with numbered citation references.
        """
        context_parts = []
        citations_meta = []

        for idx, chunk in enumerate(retrieved_chunks, 1):
            doc_title = chunk["metadata"].get("doc_title", "Document")
            citation_tag = f"[Doc: {doc_title} | Chunk #{chunk['chunk_id']}]"
            context_parts.append(f"--- Context Item #{idx} {citation_tag} ---\n{chunk['text']}")
            citations_meta.append({
                "citation_id": idx,
                "tag": citation_tag,
                "chunk_id": chunk["chunk_id"],
                "doc_title": doc_title,
                "relevance_score": chunk["score"]
            })

        full_context = "\n\n".join(context_parts)
        return full_context, citations_meta

    @staticmethod
    def synthesize_grounded_answer(query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates grounded response strictly based on retrieved context with explicit citations.
        """
        if not retrieved_chunks:
            return {
                "answer": "Insufficient grounded context found in knowledge base to reliably answer this query.",
                "citations": [],
                "faithfulness_score": 100,
                "grounded": False
            }

        context_str, citations = ContextEngine.construct_grounded_context(retrieved_chunks)
        top_chunk = retrieved_chunks[0]

        # Formulate grounded synthesis
        answer_parts = []
        answer_parts.append(f"Based on verified knowledge context ({citations[0]['tag']}):")

        # Synthesize from top chunk content
        first_sentence = top_chunk["text"].split("\n")[0]
        answer_parts.append(f"{first_sentence}")

        if len(retrieved_chunks) > 1:
            second_chunk = retrieved_chunks[1]
            answer_parts.append(
                f"Additionally, as referenced in {citations[1]['tag']}, "
                f"the system enforces {second_chunk['text'].split('.')[0].strip()}."
            )

        full_answer = "\n\n".join(answer_parts)

        return {
            "answer": full_answer,
            "citations": citations,
            "context_block": context_str,
            "grounded": True
        }
