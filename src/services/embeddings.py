"""Embedding service wrapper for sentence-transformers."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Default model - lightweight and fast
DEFAULT_MODEL = "all-MiniLM-L6-v2"


class EmbeddingService:
    """Wrapper for sentence-transformers embedding model."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedding service.

        Args:
            model_name: Model to use. Defaults to all-MiniLM-L6-v2.
        """
        self.model_name = model_name or DEFAULT_MODEL
        self._model = None

    @property
    def model(self):
        """Lazy-load the model on first use."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded. Dimensions: {self.dimensions}")
        return self._model

    @property
    def dimensions(self) -> int:
        """Get embedding dimensions."""
        return self.model.get_sentence_embedding_dimension()

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors.
        """
        if not texts:
            return []

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_single(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed.

        Returns:
            Embedding vector.
        """
        result = self.embed([text])
        return result[0] if result else []
