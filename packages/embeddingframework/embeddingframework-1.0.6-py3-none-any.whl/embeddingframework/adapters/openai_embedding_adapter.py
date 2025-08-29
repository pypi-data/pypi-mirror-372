from typing import List
from .base import EmbeddingAdapter
import openai
import os


class OpenAIEmbeddingAdapter(EmbeddingAdapter):
    def connect(self):
        """Dummy connect method for testing to satisfy ABC."""
        print("Connected to OpenAI Embedding API (dummy).")
        return True

    """Adapter for OpenAI embedding models."""
    def __init__(self, model: str = "text-embedding-ada-002", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided via parameter or OPENAI_API_KEY environment variable.")
        openai.api_key = self.api_key
        self.client = None

    def connect(self):
        """Dummy connect method for testing."""
        print("Connected to OpenAI Embedding API (dummy).")
        self.client = openai
        return True

    def embed(self, text: str) -> List[float]:
        response = openai.Embedding.create(model=self.model, input=text)
        return response["data"][0]["embedding"]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts and return list of embeddings."""
        response = openai.Embedding.create(model=self.model, input=texts)
        return [item["embedding"] for item in response["data"]]
