"""OpenAI embedding provider."""

from typing import Any, List, Optional

import numpy as np

from .base import EmbeddingProvider

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(EmbeddingProvider):
    """OpenAI embedding provider."""

    def __init__(
        self, api_key: str, model: str = "text-embedding-ada-002", **kwargs: Any
    ) -> None:
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name for embeddings
            **kwargs: Additional configuration
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package is required for OpenAI provider. Install with: pip install openai"
            )

        super().__init__(**kwargs)
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding from OpenAI API."""
        try:
            response = self.client.embeddings.create(input=text, model=self.model)
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"Error getting embedding from OpenAI: {e}")
            return None

    def get_embeddings(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Get embeddings for multiple texts in batch."""
        try:
            response = self.client.embeddings.create(input=texts, model=self.model)
            return [np.array(item.embedding) for item in response.data]
        except Exception as e:
            print(f"Error getting batch embeddings from OpenAI: {e}")
            return [None] * len(texts)
