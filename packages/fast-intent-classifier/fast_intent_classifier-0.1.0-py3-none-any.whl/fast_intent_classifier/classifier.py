"""Fast Intent Classifier using embedding vectors."""

import json
import time
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import numpy as np

from .providers.aws_bedrock import AWSBedrockProvider
from .providers.azure_openai import AzureOpenAIProvider
from .providers.base import EmbeddingProvider
from .providers.custom import CustomProvider
from .providers.ollama import OllamaProvider
from .providers.openai import OpenAIProvider


class FastIntentClassifier:
    """A fast intent classifier using embedding vectors for intent detection."""

    def __init__(
        self, provider: Union[str, EmbeddingProvider] = "ollama", **kwargs: Any
    ) -> None:
        """
        Initialize the FastIntentClassifier.

        Args:
            provider: Either a provider name string or EmbeddingProvider instance
            **kwargs: Configuration passed to the provider
        """
        if isinstance(provider, str):
            self.provider = self._create_provider(provider, **kwargs)
        elif isinstance(provider, EmbeddingProvider):
            self.provider = provider
        else:
            raise ValueError("provider must be a string or EmbeddingProvider instance")

        self.intent_vectors: Dict[str, np.ndarray] = {}
        self.intents: Dict[str, List[str]] = {}

    def _create_provider(self, provider_name: str, **kwargs: Any) -> EmbeddingProvider:
        """Create provider instance from name."""
        providers: Dict[str, Type[EmbeddingProvider]] = {
            "ollama": OllamaProvider,
            "openai": OpenAIProvider,
            "azure_openai": AzureOpenAIProvider,
            "aws_bedrock": AWSBedrockProvider,
            "custom": CustomProvider,
        }

        if provider_name not in providers:
            available = ", ".join(providers.keys())
            raise ValueError(
                f"Unsupported provider '{provider_name}'. Available: {available}"
            )

        provider_class = providers[provider_name]
        return provider_class(**kwargs)

    def _embed_multiple(self, texts: List[str]) -> np.ndarray:
        """Embed multiple texts and return as numpy array."""
        embeddings = self.provider.get_embeddings(texts)
        valid_embeddings = [emb for emb in embeddings if emb is not None]
        return np.vstack(valid_embeddings) if valid_embeddings else np.array([])

    def load_intents(self, intents: Union[Dict[str, List[str]], str]) -> bool:
        """
        Load intents from a dictionary or JSON file.

        Args:
            intents: Dictionary with intent keys and list of example strings as values,
                    or path to JSON file containing the intents

        Returns:
            bool: True if intents were loaded successfully, False otherwise
        """
        try:
            if isinstance(intents, str):
                # Load from JSON file
                with open(intents, "r", encoding="utf-8") as f:
                    intents_data = json.load(f)
            else:
                intents_data = intents

            self.intents = intents_data
            self.intent_vectors = {}

            print(f"Loading {len(intents_data)} intents...")

            for intent_name, examples in intents_data.items():
                if not examples:
                    print(f"Warning: Intent '{intent_name}' has no examples")
                    continue

                print(
                    f"Processing intent '{intent_name}' with {len(examples)} examples..."
                )

                # Get embeddings for all examples
                embeddings = self._embed_multiple(examples)

                if embeddings.size > 0:
                    # Create intent vector by averaging all example embeddings
                    intent_vector = embeddings.mean(axis=0)
                    # Normalize the vector
                    intent_vector = intent_vector / np.linalg.norm(intent_vector)
                    self.intent_vectors[intent_name] = intent_vector
                    print(f"✅ Intent '{intent_name}' vector created")
                else:
                    print(f"❌ Failed to create vector for intent '{intent_name}'")

            print(f"🎉 Successfully loaded {len(self.intent_vectors)} intent vectors!")
            return True

        except Exception as e:
            print(f"Error loading intents: {e}")
            return False

    def detect_intent(
        self, message: str, return_confidence: bool = True
    ) -> Union[str, Tuple[str, float]]:
        """
        Detect the intent of a message.

        Args:
            message: The input message to classify
            return_confidence: Whether to return confidence score along with intent

        Returns:
            str: Intent name if return_confidence is False
            Tuple[str, float]: (intent_name, confidence_score) if return_confidence is True
        """
        if not self.intent_vectors:
            raise ValueError("No intents loaded. Call load_intents() first.")

        start_time = time.time()

        # Get embedding for the message
        message_embedding = self.provider.get_embedding(message)
        if message_embedding is None:
            if return_confidence:
                return "unknown", 0.0
            return "unknown"

        # Normalize the message vector
        message_vector = message_embedding / np.linalg.norm(message_embedding)

        # Calculate similarity with each intent vector
        scores = {}
        for intent_name, intent_vector in self.intent_vectors.items():
            similarity = float(np.dot(message_vector, intent_vector))
            scores[intent_name] = similarity

        # Find the best match
        best_intent = max(scores, key=lambda x: scores[x])
        confidence = scores[best_intent]

        elapsed_ms = (time.time() - start_time) * 1000
        print(f"Classification took {elapsed_ms:.2f} ms")

        if return_confidence:
            return best_intent, confidence
        return best_intent

    def get_all_scores(self, message: str) -> Dict[str, float]:
        """
        Get similarity scores for all intents.

        Args:
            message: The input message to classify

        Returns:
            Dict[str, float]: Dictionary mapping intent names to similarity scores
        """
        if not self.intent_vectors:
            raise ValueError("No intents loaded. Call load_intents() first.")

        message_embedding = self.provider.get_embedding(message)
        if message_embedding is None:
            return {}

        message_vector = message_embedding / np.linalg.norm(message_embedding)

        scores = {}
        for intent_name, intent_vector in self.intent_vectors.items():
            similarity = float(np.dot(message_vector, intent_vector))
            scores[intent_name] = similarity

        return scores

    def get_loaded_intents(self) -> List[str]:
        """Get list of loaded intent names."""
        return list(self.intent_vectors.keys())

    def load_intent_vectors(
        self, intent_vectors: Union[Dict[str, List[float]], str]
    ) -> bool:
        """
        Load pre-computed intent vectors directly.

        Args:
            intent_vectors: Dictionary with intent names as keys and embedding vectors as values,
                           or path to JSON file containing the vectors

        Returns:
            bool: True if vectors were loaded successfully
        """
        try:
            if isinstance(intent_vectors, str):
                # Load from JSON file
                with open(intent_vectors, "r", encoding="utf-8") as f:
                    vectors_data = json.load(f)
            else:
                vectors_data = intent_vectors

            self.intent_vectors = {}

            print(f"Loading {len(vectors_data)} pre-computed intent vectors...")

            for intent_name, vector_data in vectors_data.items():
                try:
                    # Convert to numpy array and normalize
                    vector = np.array(vector_data, dtype=np.float32)
                    normalized_vector = vector / np.linalg.norm(vector)
                    self.intent_vectors[intent_name] = normalized_vector
                    print(
                        f"✅ Intent vector '{intent_name}' loaded (dimension: {len(vector)})"
                    )
                except Exception as e:
                    print(f"❌ Failed to load vector for intent '{intent_name}': {e}")
                    continue

            # Clear the examples since we're loading vectors directly
            self.intents = {intent: [] for intent in self.intent_vectors.keys()}

            print(f"🎉 Successfully loaded {len(self.intent_vectors)} intent vectors!")
            return len(self.intent_vectors) > 0

        except Exception as e:
            print(f"Error loading intent vectors: {e}")
            return False

    def save_intent_vectors(self, filepath: str) -> bool:
        """
        Save the current intent vectors to a JSON file.

        Args:
            filepath: Path to save the vectors

        Returns:
            bool: True if vectors were saved successfully
        """
        if not self.intent_vectors:
            print("No intent vectors to save")
            return False

        try:
            # Convert numpy arrays to lists for JSON serialization
            vectors_data = {
                intent: vector.tolist()
                for intent, vector in self.intent_vectors.items()
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(vectors_data, f, indent=2)

            print(f"✅ Saved {len(self.intent_vectors)} intent vectors to {filepath}")
            return True

        except Exception as e:
            print(f"Error saving intent vectors: {e}")
            return False

    def get_intent_vector(self, intent_name: str) -> Optional[np.ndarray]:
        """
        Get the vector for a specific intent.

        Args:
            intent_name: Name of the intent

        Returns:
            Optional[np.ndarray]: The intent vector or None if not found
        """
        return self.intent_vectors.get(intent_name)

    def add_intent_vector(
        self,
        intent_name: str,
        vector: Union[List[float], np.ndarray],
        normalize: bool = True,
    ) -> bool:
        """
        Add a single intent vector.

        Args:
            intent_name: Name of the intent
            vector: The embedding vector
            normalize: Whether to normalize the vector (default True)

        Returns:
            bool: True if vector was added successfully
        """
        try:
            vector_array = np.array(vector, dtype=np.float32)

            if normalize:
                vector_array = vector_array / np.linalg.norm(vector_array)

            self.intent_vectors[intent_name] = vector_array

            # Add empty examples list if not exists
            if intent_name not in self.intents:
                self.intents[intent_name] = []

            print(
                f"✅ Added intent vector '{intent_name}' (dimension: {len(vector_array)})"
            )
            return True

        except Exception as e:
            print(f"Error adding intent vector '{intent_name}': {e}")
            return False
