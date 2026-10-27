"""
In-Memory Vector Store and Similarity Index for GroundTrace.
Supports dense cosine similarity, top-k retrieval, threshold filtering, and metadata separation.
"""
import math
from typing import List, Dict, Any, Tuple
from ..ingestion.chunker import Chunk


class VectorStoreIndex:
    """
    High-performance in-memory vector index with module separation and cosine similarity search.
    """

    def __init__(self):
        self.vectors: Dict[str, List[float]] = {}
        self.chunks: Dict[str, Chunk] = {}
        self.doc_index: Dict[str, List[str]] = {}

    def insert(self, chunk: Chunk, vector: List[float]) -> None:
        self.vectors[chunk.chunk_id] = vector
        self.chunks[chunk.chunk_id] = chunk

        if chunk.doc_id not in self.doc_index:
            self.doc_index[chunk.doc_id] = []
        self.doc_index[chunk.doc_id].append(chunk.chunk_id)

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if len(vec_a) != len(vec_b):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        return max(0.0, min(1.0, dot_product))

    def search(
        self,
        query_vector: List[float],
        top_k: int = 3,
        min_threshold: float = 0.05,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        scored_results: List[Tuple[float, str]] = []

        for chunk_id, vec in self.vectors.items():
            chunk = self.chunks[chunk_id]

            # Apply metadata filters if specified
            if filter_metadata:
                skip = False
                for k, v in filter_metadata.items():
                    if chunk.metadata.get(k) != v:
                        skip = True
                        break
                if skip:
                    continue

            score = self._cosine_similarity(query_vector, vec)
            if score >= min_threshold:
                scored_results.append((score, chunk_id))

        # Sort descending by similarity score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        top_results = scored_results[:top_k]

        return [
            {
                "chunk_id": cid,
                "score": round(score, 4),
                "text": self.chunks[cid].text,
                "metadata": self.chunks[cid].metadata,
                "doc_id": self.chunks[cid].doc_id,
            }
            for score, cid in top_results
        ]

    def clear(self) -> None:
        self.vectors.clear()
        self.chunks.clear()
        self.doc_index.clear()

    def stats(self) -> Dict[str, int]:
        return {
            "total_chunks_indexed": len(self.chunks),
            "total_documents": len(self.doc_index)
        }
