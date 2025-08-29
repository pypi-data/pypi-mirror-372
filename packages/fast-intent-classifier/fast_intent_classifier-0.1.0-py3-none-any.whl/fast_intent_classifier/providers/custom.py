"""Custom embedding provider for user-defined implementations."""

from typing import Any, Callable, Optional

import numpy as np

from .base import EmbeddingProvider


class CustomProvider(EmbeddingProvider):
    """Custom embedding provider for user-defined embedding functions."""

    def __init__(
        self, embedding_function: Callable[[str], Optional[np.ndarray]], **kwargs: Any
    ) -> None:
        """
        Initialize custom provider.

        Args:
            embedding_function: A callable that takes a string and returns embedding array or None
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self.embedding_function = embedding_function

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding using custom function."""
        try:
            return self.embedding_function(text)
        except Exception as e:
            print(f"Error in custom embedding function: {e}")
            return None
