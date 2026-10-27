"""
FastEmbed Semantic Vector Generator for GroundTrace.
Generates normalized dense embedding vectors for fast, memory-efficient vector search.
"""
import math
import hashlib
from typing import List


class FastEmbedder:
    """
    Lightweight, high-throughput vector embedding generator.
    Produces L2-normalized 128-dimensional dense vectors using multi-gram hashing and semantic term projection.
    """

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        tokens = text.lower().replace("\n", " ").split()
        if not tokens:
            return [0.0] * self.dimension

        vector = [0.0] * self.dimension

        # Multi-gram hashing into vector dimensions
        for i, token in enumerate(tokens):
            # Unigram projection
            h_uni = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            dim_uni = h_uni % self.dimension
            sign_uni = 1.0 if (h_uni // self.dimension) % 2 == 0 else -1.0
            vector[dim_uni] += sign_uni * 1.0

            # Bigram projection
            if i < len(tokens) - 1:
                bigram = f"{token}_{tokens[i+1]}"
                h_bi = int(hashlib.md5(bigram.encode("utf-8")).hexdigest(), 16)
                dim_bi = h_bi % self.dimension
                sign_bi = 1.0 if (h_bi // self.dimension) % 2 == 0 else -1.0
                vector[dim_bi] += sign_bi * 1.5

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [round(v / norm, 5) for v in vector]

        return vector

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]
