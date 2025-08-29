from typing import List
import openai
import requests
import logging

from embeddingframework.adapters.base import EmbeddingAdapter

# Registry for embedding providers
_provider_registry = {}

def register_provider(name: str, provider_cls):
    """Register a provider class by name."""
    _provider_registry[name] = provider_cls

def get_provider(name: str):
    """Retrieve a registered provider class by name."""
    return _provider_registry.get(name)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class OpenAIEmbeddingAdapter(EmbeddingAdapter):
    """Adapter for OpenAI embeddings."""
    def __init__(self, model: str = "text-embedding-ada-002", api_key: str = None):
        self.model = model
        self.api_key = api_key or openai.api_key

    def embed(self, text: str) -> List[float]:
        try:
            response = openai.Embedding.create(model=self.model, input=text, api_key=self.api_key)
            return response['data'][0]['embedding']
        except Exception as e:
            logging.error(f"OpenAI embedding failed: {e}")
            raise

class HuggingFaceEmbeddingAdapter(EmbeddingAdapter):
    """Adapter for HuggingFace embeddings using transformers pipeline with pooling options and device management."""
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: str = None, pooling: str = "mean"):
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
        except ImportError as e:
            logging.error("Transformers library is required for HuggingFaceEmbeddingAdapter. Install with `pip install transformers`.")
            raise

        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.pooling = pooling
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.torch = torch

    def embed(self, text: str) -> List[float]:
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(self.device)
            with self.torch.no_grad():
                outputs = self.model(**inputs)
            if self.pooling == "mean":
                embeddings = outputs.last_hidden_state.mean(dim=1)
            elif self.pooling == "cls":
                embeddings = outputs.last_hidden_state[:, 0, :]
            else:
                raise ValueError(f"Unsupported pooling method: {self.pooling}")
            return embeddings.squeeze().tolist()
        except Exception as e:
            logging.error(f"HuggingFace embedding failed: {e}")
            raise

class LocalEmbeddingAdapter(EmbeddingAdapter):
    """Adapter for local embedding models."""
    def __init__(self, model_callable):
        self.model_callable = model_callable

    def embed(self, text: str) -> List[float]:
        try:
            return self.model_callable(text)
        except Exception as e:
            logging.error(f"Local embedding failed: {e}")
            raise
