"""Azure OpenAI embedding provider."""

from typing import Any, List, Optional

import numpy as np

from .base import EmbeddingProvider

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AzureOpenAIProvider(EmbeddingProvider):
    """Azure OpenAI embedding provider."""

    def __init__(
        self,
        api_key: str,
        azure_endpoint: str,
        api_version: str = "2024-02-01",
        model: str = "text-embedding-ada-002",
        **kwargs: Any,
    ) -> None:
        """
        Initialize Azure OpenAI provider.

        Args:
            api_key: Azure OpenAI API key
            azure_endpoint: Azure OpenAI endpoint URL (e.g., https://your-resource.openai.azure.com/)
            api_version: API version to use
            model: Model # The `deployment` parameter in the `AzureOpenAIProvider` class constructor
            # is used to specify the model deployment name for embeddings. This parameter
            # allows you to specify which specific model deployment you want to use for
            # generating embeddings when interacting with the Azure OpenAI API. By
            # providing the `deployment` parameter, you can target a specific model
            # configuration or version for your embedding requests.
            deployment name for embeddings
            **kwargs: Additional configuration
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package is required for Azure OpenAI provider. Install with: pip install openai"
            )

        super().__init__(**kwargs)
        self.client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )
        self.model = model

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding from Azure OpenAI API."""
        try:
            response = self.client.embeddings.create(input=text, model=self.model)
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"Error getting embedding from Azure OpenAI: {e}")
            return None

    def get_embeddings(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Get embeddings for multiple texts in batch."""
        try:
            response = self.client.embeddings.create(input=texts, model=self.model)
            return [np.array(item.embedding) for item in response.data]
        except Exception as e:
            print(f"Error getting batch embeddings from Azure OpenAI: {e}")
            return [None] * len(texts)