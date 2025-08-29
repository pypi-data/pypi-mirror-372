"""Ollama embedding provider."""

from typing import Any, Optional

import numpy as np
import requests

from .base import EmbeddingProvider


class OllamaProvider(EmbeddingProvider):
    """Ollama embedding provider."""

    def __init__(
        self,
        model: str = "nomic-embed-text",
        api_url: str = "http://localhost:11434/api/embeddings",
        **kwargs: Any,
    ) -> None:
        """
        Initialize Ollama provider.

        Args:
            model: Model name for embeddings
            api_url: Ollama API URL
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self.model = model
        self.api_url = api_url

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding from Ollama API."""
        payload = {"model": self.model, "prompt": text}

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return np.array(data["embedding"])
        except requests.exceptions.RequestException as e:
            print(f"Error getting embedding from Ollama: {e}")
            return None
