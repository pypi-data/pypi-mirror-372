"""Embedding providers for FastIntentClassifier."""

from .anthropic import AnthropicProvider
from .aws_bedrock import AWSBedrockProvider
from .azure_openai import AzureOpenAIProvider
from .base import EmbeddingProvider
from .custom import CustomProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider

__all__ = [
    "EmbeddingProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "AzureOpenAIProvider",
    "AnthropicProvider",
    "AWSBedrockProvider",
    "CustomProvider",
]
