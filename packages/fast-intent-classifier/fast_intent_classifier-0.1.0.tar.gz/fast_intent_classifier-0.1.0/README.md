# Fast Intent Classifier

A fast and lightweight intent classifier using embedding vectors for natural language understanding.

## Features

- ⚡ **Fast**: Uses pre-computed embedding vectors for quick intent classification
- 🎯 **Accurate**: Leverages semantic similarity using embeddings
- 🔧 **Easy to use**: Simple API with just two main methods
- 🌐 **Flexible**: Supports multiple embedding providers (Ollama, OpenAI, Azure OpenAI, AWS Bedrock, Anthropic, Custom)
- 📦 **Lightweight**: Minimal dependencies

## Installation

```bash
pip install fast-intent-classifier
```

## Installation Options

```bash
# Basic installation (includes Ollama support)
pip install fast-intent-classifier

# With OpenAI support (includes Azure OpenAI)
pip install fast-intent-classifier[openai]

# With AWS Bedrock support  
pip install fast-intent-classifier[aws]

# With Anthropic support
pip install fast-intent-classifier[anthropic]

# With all providers
pip install fast-intent-classifier[all]
```

## Quick Start

### Using Ollama (Default)
```python
from fast_intent_classifier import FastIntentClassifier

# Initialize with Ollama (default)
classifier = FastIntentClassifier()

# Define your intents with diverse examples
intents = {
    "greeting": [
        "hi there", "hello", "good morning", "hey", "greetings", 
        "what's up", "good afternoon", "good evening"
    ],
    "order_status": [
        "where is my order?", "track my package", "order status",
        "when will my order arrive?", "check delivery status",
        "has my order shipped?", "where's my delivery?"
    ],
    "cancel_order": [
        "cancel my order", "I want to cancel", "stop my order",
        "cancel the purchase", "abort my order", "don't ship my order"
    ],
    "refund": [
        "I want a refund", "return my money", "refund request",
        "give me my money back", "I want to return this", "refund policy"
    ],
    "support": [
        "I need help", "technical support", "customer service",
        "help me", "assistance needed", "I have a problem"
    ]
}

# Load and classify
classifier.load_intents(intents)
intent, confidence = classifier.detect_intent("hello there!")
print(f"Intent: {intent}, Confidence: {confidence:.4f}")
```

## Best Practices & Advanced Usage

### Using Confidence Thresholds

The classifier returns confidence scores that help you determine if the prediction is reliable. It's recommended to set confidence thresholds and implement fallback strategies:

```python
def classify_with_threshold(classifier, message, threshold=0.7):
    intent, confidence = classifier.detect_intent(message)
    
    if confidence >= threshold:
        return intent, confidence, "high_confidence"
    elif confidence >= 0.4:
        return intent, confidence, "medium_confidence"  
    else:
        return None, confidence, "low_confidence"

# Example usage
message = "I want to cancel my order and get refund"
intent, confidence, confidence_level = classify_with_threshold(classifier, message)

print(f"Intent: {intent}")
print(f"Confidence: {confidence:.4f}")
print(f"Confidence Level: {confidence_level}")

# Handle based on confidence level
if confidence_level == "low_confidence":
    print("⚠️  Low confidence - consider LLM fallback or human handoff")
elif confidence_level == "medium_confidence":
    print("🤔 Medium confidence - might need clarification")
else:
    print("✅ High confidence - proceed with intent")
```

### LLM Fallback Strategy

For low-confidence predictions, consider falling back to a more powerful LLM:

```python
import openai  # or your preferred LLM client

def classify_with_llm_fallback(classifier, message, threshold=0.7):
    intent, confidence = classifier.detect_intent(message)
    
    if confidence >= threshold:
        return intent, confidence, "embedding"
    else:
        # Fallback to LLM for better accuracy
        return classify_with_llm(message), confidence, "llm_fallback"

def classify_with_llm(message):
    # Example using OpenAI - adapt to your preferred LLM
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system", 
            "content": f"Classify this message into one of these intents: {list(intents.keys())}. Return only the intent name."
        }, {
            "role": "user", 
            "content": message
        }]
    )
    return response.choices[0].message.content.strip()

# Usage
intent, confidence, method = classify_with_llm_fallback(classifier, "complex ambiguous message")
print(f"Classified as: {intent} (method: {method}, confidence: {confidence:.4f})")
```

### Determining Optimal Thresholds

The optimal threshold depends on your specific use case and dataset. Here's how to find the right balance:

```python
def evaluate_thresholds(classifier, test_data, thresholds=[0.5, 0.6, 0.7, 0.8, 0.9]):
    """
    Test different threshold values to find optimal balance between
    precision and coverage for your specific use case.
    
    test_data: List of (message, expected_intent) tuples
    """
    results = {}
    
    for threshold in thresholds:
        correct_high_conf = 0
        total_high_conf = 0
        total_fallbacks = 0
        
        for message, expected in test_data:
            intent, confidence = classifier.detect_intent(message)
            
            if confidence >= threshold:
                total_high_conf += 1
                if intent == expected:
                    correct_high_conf += 1
            else:
                total_fallbacks += 1
        
        precision = correct_high_conf / max(1, total_high_conf)
        coverage = total_high_conf / len(test_data)
        fallback_rate = total_fallbacks / len(test_data)
        
        results[threshold] = {
            'precision': precision,
            'coverage': coverage, 
            'fallback_rate': fallback_rate
        }
    
    return results

# Example: Find optimal threshold for your data
# test_data = [("hello", "greeting"), ("cancel order", "cancel_order"), ...]  
# threshold_results = evaluate_thresholds(classifier, test_data)
```

### Handling Similar Intents

When dealing with very similar intents like `cancel_order` and `refund`, consider these strategies:

#### 1. **Use More Diverse Training Examples**
```python
intents = {
    "cancel_order": [
        "cancel my order", "stop my order", "abort my purchase",
        "I don't want this order anymore", "cancel the shipment",
        "please cancel before shipping", "halt my order"
    ],
    "refund": [  
        "I want my money back", "refund my purchase", "return and refund",
        "I want to return this for money", "refund to my card",
        "give me a refund", "I need my money back"
    ]
}
```

#### 2. **Monitor Confusion Between Similar Intents**
```python
def analyze_intent_confusion(classifier, messages):
    """Analyze which intents are often confused with each other"""
    confusion_matrix = {}
    
    for message in messages:
        scores = classifier.get_all_scores(message)
        # Get top 2 intents
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_scores) >= 2:
            top_intent = sorted_scores[0][0]
            second_intent = sorted_scores[1][0] 
            score_diff = sorted_scores[0][1] - sorted_scores[1][1]
            
            # Flag potential confusion when scores are very close
            if score_diff < 0.1:  # Adjust threshold as needed
                key = f"{top_intent} vs {second_intent}"
                if key not in confusion_matrix:
                    confusion_matrix[key] = []
                confusion_matrix[key].append({
                    'message': message,
                    'score_difference': score_diff,
                    'scores': {top_intent: sorted_scores[0][1], second_intent: sorted_scores[1][1]}
                })
    
    return confusion_matrix

# Example usage
test_messages = [
    "I want to cancel and get money back",
    "cancel my order for refund", 
    "stop my purchase and refund"
]

confusion_analysis = analyze_intent_confusion(classifier, test_messages)
for confusion_pair, examples in confusion_analysis.items():
    print(f"\n⚠️  Potential confusion: {confusion_pair}")
    for example in examples[:3]:  # Show top 3 examples
        print(f"  Message: '{example['message']}'")
        print(f"  Score difference: {example['score_difference']:.4f}")
```

#### 3. **Consider Intent Hierarchies**
For very similar intents, you might want to group them under a parent category:
```python
# Option 1: Combine similar intents during training
intents = {
    "order_modification": [  # Combines cancel + refund
        "cancel my order", "I want a refund", "stop my order",
        "return my money", "cancel and refund", "abort purchase"
    ]
}

# Option 2: Use post-processing to handle ambiguous cases
def handle_similar_intents(intent, confidence, message):
    if intent in ["cancel_order", "refund"] and confidence < 0.8:
        # For ambiguous cases, ask for clarification or use business logic
        return "order_modification", confidence
    return intent, confidence
```

**Key Recommendations:**
- Start with a threshold around **0.7** and adjust based on your evaluation results
- Monitor the fallback rate - aim for less than 20% if possible
- For production systems, always implement human handoff for very low confidence cases
- Use A/B testing to validate threshold changes in production
- Consider business impact: false positives vs false negatives for each intent

### Loading Pre-computed Vectors
If you already have embedding vectors, you can load them directly:

```python
# Load from dictionary
intent_vectors = {
    "greeting": [0.1, 0.2, 0.3, ...],  # Your embedding vector
    "goodbye": [-0.1, -0.2, -0.3, ...],
    "help": [0.5, 0.6, 0.7, ...]
}
classifier.load_intent_vectors(intent_vectors)

# Or load from JSON file
classifier.load_intent_vectors("my_vectors.json")

# Add individual vectors
classifier.add_intent_vector("new_intent", [0.1, 0.2, 0.3, ...])

# Save trained vectors for later use
classifier.save_intent_vectors("trained_model.json")
```

### Using OpenAI
```python
# Initialize with OpenAI
classifier = FastIntentClassifier(
    provider="openai",
    api_key="your-openai-api-key",
    model="text-embedding-ada-002"
)

classifier.load_intents(intents)
intent, confidence = classifier.detect_intent("hello there!")
```

### Using Azure OpenAI
```python
# Initialize with Azure OpenAI
classifier = FastIntentClassifier(
    provider="azure_openai",
    api_key="your-azure-openai-api-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_version="2024-02-01",
    model="your-deployment-name"
)

classifier.load_intents(intents)
intent, confidence = classifier.detect_intent("hello there!")
```

### Using AWS Bedrock
```python
# Initialize with AWS Bedrock
classifier = FastIntentClassifier(
    provider="aws_bedrock",
    region_name="us-east-1",
    model_id="amazon.titan-embed-text-v1"
)

classifier.load_intents(intents)
intent, confidence = classifier.detect_intent("hello there!")
```

### Using Custom Provider
```python
import numpy as np
from fast_intent_classifier.providers import CustomProvider

# Define your custom embedding function
def my_embedding_function(text: str) -> np.ndarray:
    # Your custom embedding logic here
    # This example uses sentence-transformers
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode(text)

# Use custom provider
custom_provider = CustomProvider(embedding_function=my_embedding_function)
classifier = FastIntentClassifier(provider=custom_provider)

classifier.load_intents(intents)
intent, confidence = classifier.detect_intent("hello there!")
```

## Embedding Providers

Fast Intent Classifier supports multiple embedding providers to suit different requirements and environments. Each provider has its own configuration options and trade-offs.

### Provider Overview

| Provider | Type | Setup Complexity | Cost | Quality | Use Case |
|----------|------|-----------------|------|---------|----------|
| **Ollama** | Local | Low | Free | Good | Development, Privacy |
| **OpenAI** | API | Low | Pay-per-use | Excellent | Production, High accuracy |
| **Azure OpenAI** | API | Medium | Pay-per-use | Excellent | Enterprise, Azure ecosystem |
| **AWS Bedrock** | API | High | Pay-per-use | Excellent | Enterprise, AWS ecosystem |
| **Anthropic** | API | Low | Pay-per-use | Excellent | Coming soon |
| **Custom** | Varies | High | Varies | Varies | Specific requirements |

### Detailed Provider Configuration

#### 1. Ollama Provider (Default)

**Best for:** Local development, privacy-focused applications, offline usage

```python
classifier = FastIntentClassifier(
    provider="ollama",
    model="nomic-embed-text",  # Default model
    api_url="http://localhost:11434/api/embeddings"  # Default URL
)
```

**Setup Requirements:**
1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
2. Pull embedding model: `ollama pull nomic-embed-text`
3. Start Ollama service: `ollama serve`

**Configuration Options:**
- `model`: Embedding model name (default: "nomic-embed-text")
- `api_url`: Ollama API endpoint (default: "http://localhost:11434/api/embeddings")

**Pros:**
- ✅ Free to use
- ✅ Runs locally (privacy)
- ✅ No API keys required
- ✅ Works offline
- ✅ Multiple models available

**Cons:**
- ❌ Requires local setup
- ❌ Performance depends on hardware
- ❌ Limited to available Ollama models

#### 2. OpenAI Provider

**Best for:** Production applications requiring high-quality embeddings

```python
classifier = FastIntentClassifier(
    provider="openai",
    api_key="sk-your-openai-api-key",
    model="text-embedding-3-large",  # Latest model
    # model="text-embedding-ada-002",  # Legacy model
)
```

**Setup Requirements:**
1. Create OpenAI account at https://platform.openai.com
2. Generate API key
3. Install: `pip install openai`

**Configuration Options:**
- `api_key`: OpenAI API key (required)
- `model`: Embedding model (default: "text-embedding-ada-002")
  - `text-embedding-3-large`: Highest quality (3072 dimensions)
  - `text-embedding-3-small`: Balanced performance (1536 dimensions)
  - `text-embedding-ada-002`: Legacy model (1536 dimensions)

**Pros:**
- ✅ Excellent quality
- ✅ Fast API responses
- ✅ Batch processing support
- ✅ Reliable service
- ✅ Latest embedding models

**Cons:**
- ❌ Costs money per token
- ❌ Requires internet connection
- ❌ Usage limits apply

#### 3. Azure OpenAI Provider

**Best for:** Enterprise applications using Azure cloud infrastructure

```python
classifier = FastIntentClassifier(
    provider="azure_openai",
    api_key="your-azure-openai-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_version="2024-02-01",
    model="text-embedding-ada-002"  # Your deployment name
)
```

**Setup Requirements:**
1. Create Azure OpenAI resource in Azure Portal
2. Deploy an embedding model (e.g., text-embedding-ada-002)
3. Get API key and endpoint
4. Install: `pip install openai`

**Configuration Options:**
- `api_key`: Azure OpenAI API key (required)
- `azure_endpoint`: Your Azure OpenAI endpoint URL (required)
- `api_version`: API version (default: "2024-02-01")
- `model`: Deployment name (not model name!)

**Pros:**
- ✅ Enterprise-grade security
- ✅ Data residency control
- ✅ Same quality as OpenAI
- ✅ Azure integration
- ✅ SLA guarantees

**Cons:**
- ❌ More complex setup
- ❌ Costs money per token
- ❌ Requires Azure knowledge
- ❌ Limited model availability

#### 4. AWS Bedrock Provider

**Best for:** Enterprise applications using AWS infrastructure

```python
classifier = FastIntentClassifier(
    provider="aws_bedrock",
    region_name="us-east-1",
    model_id="amazon.titan-embed-text-v1",
    # Optional AWS credentials (uses default chain if not provided)
    aws_access_key_id="your-access-key",
    aws_secret_access_key="your-secret-key"
)
```

**Setup Requirements:**
1. AWS account with Bedrock access
2. Request access to embedding models in Bedrock console
3. Configure AWS credentials
4. Install: `pip install boto3`

**Configuration Options:**
- `region_name`: AWS region (default: "us-east-1")
- `model_id`: Bedrock model identifier
  - `amazon.titan-embed-text-v1`: Amazon's embedding model
  - `cohere.embed-english-v3`: Cohere's English model
  - `cohere.embed-multilingual-v3`: Cohere's multilingual model
- AWS credential parameters (optional if using IAM roles/profiles)

**Pros:**
- ✅ Enterprise features
- ✅ Multiple model options
- ✅ AWS ecosystem integration
- ✅ Scalable infrastructure
- ✅ Fine-grained access control

**Cons:**
- ❌ Complex AWS setup
- ❌ Costs money per token
- ❌ Requires AWS knowledge
- ❌ Model access approval needed

#### 5. Anthropic Provider (Coming Soon)

**Best for:** Applications requiring Claude-powered embeddings

```python
# Note: This provider is currently a placeholder
classifier = FastIntentClassifier(
    provider="anthropic",
    api_key="your-anthropic-api-key"
)
```

**Status:** Currently returns `NotImplementedError` as Anthropic doesn't provide direct embedding endpoints. This provider is reserved for future implementation.

#### 6. Custom Provider

**Best for:** Specific requirements, existing embedding models, custom logic

```python
import numpy as np
from fast_intent_classifier.providers import CustomProvider

# Option 1: Simple function
def simple_embedding(text: str) -> np.ndarray:
    # Your embedding logic
    return some_model.encode(text)

classifier = FastIntentClassifier(
    provider=CustomProvider(embedding_function=simple_embedding)
)

# Option 2: Using sentence-transformers
def sentence_transformer_embedding(text: str) -> np.ndarray:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode(text)

classifier = FastIntentClassifier(
    provider=CustomProvider(embedding_function=sentence_transformer_embedding)
)

# Option 3: Using Hugging Face transformers
def huggingface_embedding(text: str) -> np.ndarray:
    from transformers import AutoTokenizer, AutoModel
    import torch
    
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Mean pooling
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embeddings

classifier = FastIntentClassifier(
    provider=CustomProvider(embedding_function=huggingface_embedding)
)
```

**Configuration Options:**
- `embedding_function`: Callable that takes a string and returns numpy array

**Pros:**
- ✅ Complete control over embedding logic
- ✅ Use any embedding model
- ✅ Custom preprocessing/postprocessing
- ✅ No API dependencies
- ✅ Can combine multiple models

**Cons:**
- ❌ Requires implementation effort
- ❌ You manage model lifecycle
- ❌ Performance optimization needed
- ❌ Error handling responsibility

### Provider Selection Guide

**Choose Ollama if:**
- You're developing locally
- Privacy is a concern
- You want to avoid API costs
- Internet connectivity is limited

**Choose OpenAI if:**
- You want the highest quality embeddings
- You're building a production application
- Fast API response times are important
- You prefer managed services

**Choose Azure OpenAI if:**
- You're in an enterprise environment
- You need data residency control
- You're already using Azure services
- Compliance requirements are strict

**Choose AWS Bedrock if:**
- You're using AWS infrastructure
- You need multiple model options
- Enterprise features are required
- You want AWS ecosystem integration

**Choose Custom if:**
- You have specific embedding requirements
- You want to use a particular model
- You need custom preprocessing logic
- You have existing embedding infrastructure

## API Reference

### FastIntentClassifier

#### `__init__(provider="ollama", **kwargs)`

Initialize the classifier with embedding provider configuration.

**Parameters:**
- `provider` (str | EmbeddingProvider): Provider name or provider instance
- `**kwargs`: Provider-specific configuration

**Supported Providers:**
- `"ollama"`: Local Ollama instance (default)
- `"openai"`: OpenAI API (requires `api_key`)
- `"azure_openai"`: Azure OpenAI API (requires `api_key`, `azure_endpoint`)
- `"aws_bedrock"`: AWS Bedrock (requires AWS credentials)
- `"anthropic"`: Anthropic API (placeholder - not yet implemented)
- `"custom"`: Custom embedding function (requires `embedding_function`)

**Examples:**
```python
# Ollama with custom settings
FastIntentClassifier(provider="ollama", model="nomic-embed-text")

# OpenAI
FastIntentClassifier(provider="openai", api_key="sk-...", model="text-embedding-ada-002")

# Azure OpenAI
FastIntentClassifier(provider="azure_openai", api_key="...", azure_endpoint="https://...")

# AWS Bedrock  
FastIntentClassifier(provider="aws_bedrock", region_name="us-east-1")

# Custom function
FastIntentClassifier(provider="custom", embedding_function=my_func)
```

#### `load_intents(intents: Union[Dict[str, List[str]], str]) -> bool`

Load intents from a dictionary or JSON file.

**Parameters:**
- `intents`: Dictionary with intent keys and list of example strings as values, or path to JSON file

**Returns:**
- `bool`: True if intents were loaded successfully

**Example:**
```python
# From dictionary
intents = {"greeting": ["hi", "hello"], "goodbye": ["bye", "see you"]}
classifier.load_intents(intents)

# From JSON file
classifier.load_intents("intents.json")
```

#### `detect_intent(message: str, return_confidence: bool = True) -> Union[str, Tuple[str, float]]`

Detect the intent of a message.

**Parameters:**
- `message` (str): The input message to classify
- `return_confidence` (bool): Whether to return confidence score

**Returns:**
- `str`: Intent name (if return_confidence is False)
- `Tuple[str, float]`: (intent_name, confidence_score) (if return_confidence is True)

#### `get_all_scores(message: str) -> Dict[str, float]`

Get similarity scores for all intents.

**Parameters:**
- `message` (str): The input message to classify

**Returns:**
- `Dict[str, float]`: Dictionary mapping intent names to similarity scores

#### `get_loaded_intents() -> List[str]`

Get list of loaded intent names.

**Returns:**
- `List[str]`: List of intent names

#### `load_intent_vectors(intent_vectors: Union[Dict[str, List[float]], str]) -> bool`

Load pre-computed intent vectors directly.

**Parameters:**
- `intent_vectors`: Dictionary with intent names as keys and embedding vectors as values, or path to JSON file

**Returns:**
- `bool`: True if vectors were loaded successfully

#### `save_intent_vectors(filepath: str) -> bool`

Save the current intent vectors to a JSON file.

**Parameters:**
- `filepath` (str): Path to save the vectors

**Returns:**
- `bool`: True if vectors were saved successfully

#### `add_intent_vector(intent_name: str, vector: Union[List[float], np.ndarray], normalize: bool = True) -> bool`

Add a single intent vector.

**Parameters:**
- `intent_name` (str): Name of the intent
- `vector`: The embedding vector
- `normalize` (bool): Whether to normalize the vector (default True)

**Returns:**
- `bool`: True if vector was added successfully

#### `get_intent_vector(intent_name: str) -> Optional[np.ndarray]`

Get the vector for a specific intent.

**Parameters:**
- `intent_name` (str): Name of the intent

**Returns:**
- `Optional[np.ndarray]`: The intent vector or None if not found

## JSON Formats

### Intent Examples Format
Load intents with training examples:

```json
{
    "greeting": [
        "hi there",
        "hello",
        "good morning",
        "hey"
    ],
    "order_status": [
        "where is my order?",
        "order status", 
        "track my package"
    ],
    "support": [
        "I need help",
        "can you assist me",
        "technical support"
    ]
}
```

### Pre-computed Vectors Format
Load intent vectors directly:

```json
{
    "greeting": [0.1234, 0.5678, -0.2341, 0.8765, ...],
    "order_status": [0.2468, -0.1357, 0.8024, 0.3691, ...],
    "support": [-0.3691, 0.7024, -0.1468, 0.5937, ...]
}
```

**Benefits of Pre-computed Vectors:**
- ⚡ Faster startup (no embedding computation)
- 💾 Model persistence (save/load trained models)
- 🔧 Custom embeddings (use any embedding model)
- 📴 Offline mode (no API calls needed)

## Creating Custom Providers

You can create your own embedding provider by subclassing `EmbeddingProvider`:

```python
from fast_intent_classifier.providers.base import EmbeddingProvider
import numpy as np

class MyCustomProvider(EmbeddingProvider):
    def __init__(self, my_config_param="default", **kwargs):
        super().__init__(**kwargs)
        self.my_config = my_config_param
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        # Your custom embedding logic here
        # Return numpy array or None if failed
        return my_embedding_model.encode(text)

# Use your custom provider
classifier = FastIntentClassifier(provider=MyCustomProvider(my_config_param="custom_value"))
```

## Provider Comparison

| Provider | Pros | Cons | Use Case |
|----------|------|------|----------|
| **Ollama** | Free, Private, Local | Requires local setup | Development, Privacy-focused |
| **OpenAI** | High quality, Fast API | Costs money, External API | Production, High accuracy needed |
| **Azure OpenAI** | Enterprise security, Data residency | Complex setup, Costs money | Enterprise, Azure ecosystem |
| **AWS Bedrock** | Enterprise features, Scalable | Complex setup, AWS knowledge needed | Enterprise, Existing AWS infrastructure |
| **Custom** | Full control, Any model | Implementation effort | Specific requirements, Existing models |

## Requirements

- Python 3.8+
- numpy
- scikit-learn  
- requests

### Provider-specific Requirements
- **Ollama**: Ollama running locally (default setup)
- **OpenAI**: `openai` package, API key
- **Azure OpenAI**: `openai` package, API key, Azure OpenAI resource
- **AWS Bedrock**: `boto3` package, AWS credentials
- **Anthropic**: `anthropic` package, API key (when implemented)
- **Custom**: Your implementation dependencies

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## Support

- 📖 Check the examples in the repository
- 🐛 Report bugs or request features via GitHub Issues
- 💬 Ask questions in GitHub Discussions

## License

MIT License