"""Base class for embedding providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import numpy as np


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the provider with configuration."""
        self.config: Dict[str, Any] = kwargs

    @abstractmethod
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Get embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            Optional[np.ndarray]: Embedding vector or None if failed
        """
        pass

    def get_embeddings(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """
        Get embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List[Optional[np.ndarray]]: List of embedding vectors
        """
        return [self.get_embedding(text) for text in texts]

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return self.__class__.__name__
