"""AWS Bedrock embedding provider."""

import json
from typing import Any, List, Optional

import numpy as np

from .base import EmbeddingProvider

try:
    import boto3

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class AWSBedrockProvider(EmbeddingProvider):
    """AWS Bedrock embedding provider."""

    def __init__(
        self,
        region_name: str = "us-east-1",
        model_id: str = "amazon.titan-embed-text-v1",
        **kwargs: Any,
    ) -> None:
        """
        Initialize AWS Bedrock provider.

        Args:
            region_name: AWS region
            model_id: Bedrock model ID for embeddings
            **kwargs: Additional configuration (aws_access_key_id, aws_secret_access_key, etc.)
        """
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 package is required for AWS Bedrock provider. "
                "Install with: pip install boto3"
            )

        super().__init__(**kwargs)
        self.region_name = region_name
        self.model_id = model_id

        # Initialize Bedrock client
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region_name,
            **{
                k: v
                for k, v in kwargs.items()
                if k
                in ["aws_access_key_id", "aws_secret_access_key", "aws_session_token"]
            },
        )

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding from AWS Bedrock."""
        try:
            # Prepare the request body based on model
            if "titan" in self.model_id.lower():
                body = json.dumps({"inputText": text})
            else:
                # Add support for other models as needed
                body = json.dumps({"inputText": text})

            response = self.client.invoke_model(
                modelId=self.model_id, body=body, contentType="application/json"
            )

            response_body = json.loads(response["body"].read().decode("utf-8"))

            if "titan" in self.model_id.lower():
                embedding = response_body.get("embedding", [])
            else:
                # Handle other model response formats
                embedding = response_body.get("embedding", [])

            return np.array(embedding) if embedding else None

        except Exception as e:
            print(f"Error getting embedding from AWS Bedrock: {e}")
            return None

    def get_embeddings(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Get embeddings for multiple texts."""
        # AWS Bedrock typically processes one at a time
        return [self.get_embedding(text) for text in texts]
