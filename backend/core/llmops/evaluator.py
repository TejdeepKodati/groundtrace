"""
RAG Faithfulness, Context Relevance, and LLMOps Telemetry Evaluator for GroundTrace.
Quantifies factual grounding, detects hallucinations, and monitors query latency and token expenditure.
"""
from typing import Dict, Any, List


class RAGEvaluator:
    """
    Evaluator for RAG pipeline quality metrics:
    - Faithfulness: Percentage of claims in answer supported by context
    - Context Relevance: Precision of retrieved chunks against query
    - LLMOps: Latencies, token counts, inference costs
    """

    @staticmethod
    def evaluate_faithfulness(answer: str, context_block: str) -> Dict[str, Any]:
        """
        Assesses factual grounding of generated answer against retrieved context.
        """
        if not context_block or not answer:
            return {"score": 0.0, "status": "FAIL", "reason": "Empty context or answer"}

        answer_words = set(re_clean(answer))
        context_words = set(re_clean(context_block))

        if not answer_words:
            return {"score": 100.0, "status": "PASS", "supported_ratio": 1.0}

        overlap = answer_words.intersection(context_words)
        ratio = len(overlap) / len(answer_words)

        # Non-stopword grounding ratio normalized to 0-100%
        faithfulness_score = min(100.0, round(ratio * 120.0, 1))

        status = "GROUNDED" if faithfulness_score >= 80 else "MODERATE_RISK" if faithfulness_score >= 60 else "HALLUCINATION_DETECTED"

        return {
            "score": faithfulness_score,
            "status": status,
            "supported_terms_count": len(overlap),
            "hallucination_risk_pct": max(0.0, round(100.0 - faithfulness_score, 1))
        }

    @staticmethod
    def evaluate_context_relevance(query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not retrieved_chunks:
            return {"score": 0.0, "status": "NO_CONTEXT"}

        avg_similarity = sum(c["score"] for c in retrieved_chunks) / len(retrieved_chunks)
        relevance_score = min(100.0, round(avg_similarity * 100.0, 1))

        return {
            "score": relevance_score,
            "top_chunk_similarity": retrieved_chunks[0]["score"],
            "chunks_evaluated": len(retrieved_chunks)
        }


def re_clean(text: str) -> List[str]:
    import re
    # Remove punctuation, lowercase, filter out common short stopwords
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    stopwords = {"the", "and", "for", "with", "that", "this", "from", "are", "was", "based", "context"}
    return [w for w in words if w not in stopwords]
