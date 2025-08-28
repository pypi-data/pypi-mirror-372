"""
Simple vector store for Broadie memory system.
Uses minimal implementation without external dependencies.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..utils.exceptions import PersistenceError


class VectorStore:
    """
    Simple vector storage using numpy and JSON.
    Provides basic similarity search without external vector databases.
    """

    def __init__(self, storage_path: str = "vectors.json", dimension: int = 768):
        self.storage_path = Path(storage_path)
        self.dimension = dimension
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self._load_from_disk()

    def _load_from_disk(self):
        """Load vectors and metadata from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.vectors = data.get("vectors", {})
                    self.metadata = data.get("metadata", {})
            except Exception as e:
                raise PersistenceError(f"Failed to load vector store: {e}")

    def _save_to_disk(self):
        """Save vectors and metadata to disk."""
        try:
            data = {"vectors": self.vectors, "metadata": self.metadata}
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise PersistenceError(f"Failed to save vector store: {e}")

    def add_vector(
        self,
        vector_id: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Add a vector with optional metadata."""
        if len(vector) != self.dimension:
            raise ValueError(
                f"Vector dimension {len(vector)} doesn't match expected {self.dimension}"
            )

        self.vectors[vector_id] = vector
        self.metadata[vector_id] = metadata or {}
        self._save_to_disk()

    def get_vector(
        self, vector_id: str
    ) -> Optional[Tuple[List[float], Dict[str, Any]]]:
        """Get a vector and its metadata by ID."""
        if vector_id in self.vectors:
            return self.vectors[vector_id], self.metadata.get(vector_id, {})
        return None

    def remove_vector(self, vector_id: str) -> bool:
        """Remove a vector by ID."""
        if vector_id in self.vectors:
            del self.vectors[vector_id]
            if vector_id in self.metadata:
                del self.metadata[vector_id]
            self._save_to_disk()
            return True
        return False

    def search_similar(
        self, query_vector: List[float], top_k: int = 10, threshold: float = 0.0
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Find similar vectors using cosine similarity.

        Returns:
            List of (vector_id, similarity_score, metadata) tuples
        """
        if len(query_vector) != self.dimension:
            raise ValueError(
                f"Query vector dimension {len(query_vector)} doesn't match expected {self.dimension}"
            )

        if not self.vectors:
            return []

        similarities = []
        query_np = np.array(query_vector)
        query_norm = np.linalg.norm(query_np)

        if query_norm == 0:
            return []

        for vector_id, vector in self.vectors.items():
            vector_np = np.array(vector)
            vector_norm = np.linalg.norm(vector_np)

            if vector_norm == 0:
                continue

            # Cosine similarity
            similarity = np.dot(query_np, vector_np) / (query_norm * vector_norm)

            if similarity >= threshold:
                similarities.append(
                    (vector_id, float(similarity), self.metadata.get(vector_id, {}))
                )

        # Sort by similarity (descending) and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def list_all_vectors(self) -> List[str]:
        """List all vector IDs."""
        return list(self.vectors.keys())

    def count(self) -> int:
        """Get total number of vectors."""
        return len(self.vectors)

    def clear(self):
        """Clear all vectors and metadata."""
        self.vectors.clear()
        self.metadata.clear()
        self._save_to_disk()

    # Simple text-to-vector conversion (placeholder)
    # In a real implementation, you'd use a proper embedding model
    def text_to_vector(self, text: str) -> List[float]:
        """
        Convert text to vector using a simple hash-based approach.
        This is a placeholder - in production, use proper embeddings.
        """
        # Simple hash-based vector generation (not suitable for production)
        import hashlib

        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to vector of specified dimension
        vector = []
        for i in range(self.dimension):
            byte_idx = i % len(hash_bytes)
            vector.append(float(hash_bytes[byte_idx]) / 255.0)

        return vector
