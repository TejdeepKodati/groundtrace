"""
Document Ingestion and Recursive Semantic Chunking Engine for GroundTrace.
Splits text and structured telemetry into semantic chunks enriched with source metadata.
"""
import re
from typing import List, Dict, Any


class Chunk:
    def __init__(self, chunk_id: str, doc_id: str, text: str, token_estimate: int, metadata: Dict[str, Any]):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.text = text
        self.token_estimate = token_estimate
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "text": self.text,
            "token_estimate": self.token_estimate,
            "metadata": self.metadata
        }


class SemanticChunker:
    """
    Recursive boundary-aware chunker respecting paragraph and sentence boundaries.
    """

    def __init__(self, target_chunk_size: int = 500, chunk_overlap: int = 60):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc_id: str, title: str, content: str, source_type: str = "documentation") -> List[Chunk]:
        # Clean text
        clean_content = content.replace("\r\n", "\n").strip()

        # Split by double newline (paragraphs/sections)
        paragraphs = [p.strip() for p in clean_content.split("\n\n") if p.strip()]

        chunks: List[Chunk] = []
        current_text = ""
        chunk_idx = 0

        for para in paragraphs:
            para_tokens = max(1, len(para) // 4)

            if len(current_text) + len(para) < self.target_chunk_size * 4:
                current_text = f"{current_text}\n\n{para}".strip()
            else:
                if current_text:
                    token_count = max(1, len(current_text) // 4)
                    chunk_id = f"{doc_id}-chk-{chunk_idx}"
                    chunks.append(
                        Chunk(
                            chunk_id=chunk_id,
                            doc_id=doc_id,
                            text=current_text,
                            token_estimate=token_count,
                            metadata={
                                "doc_title": title,
                                "source_type": source_type,
                                "chunk_index": chunk_idx,
                            }
                        )
                    )
                    chunk_idx += 1

                # Carry over overlap
                words = current_text.split()
                overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else []
                overlap_prefix = " ".join(overlap_words)
                current_text = f"{overlap_prefix}\n\n{para}".strip()

        # Last chunk
        if current_text:
            token_count = max(1, len(current_text) // 4)
            chunk_id = f"{doc_id}-chk-{chunk_idx}"
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    text=current_text,
                    token_estimate=token_count,
                    metadata={
                        "doc_title": title,
                        "source_type": source_type,
                        "chunk_index": chunk_idx,
                    }
                )
            )

        return chunks
