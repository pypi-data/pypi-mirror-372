from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    @abstractmethod
    def connect(self):
        pass

    def disconnect(self):
        """Default disconnect implementation to satisfy abstract method requirement."""
        pass

class EmbeddingAdapter(BaseAdapter):
    @abstractmethod
    def embed(self, text: str):
        pass

    def embed_texts(self, texts):
        """Default embed_texts implementation for testing."""
        return [[0.0] * 1536 for _ in texts]


class VectorDBAdapter(BaseAdapter):
    def insert_embeddings(self, ids, embeddings, metadatas):
        """Default insert_embeddings implementation for testing."""
        pass

    def query(self, query_embeddings, n_results=5):
        """Default query implementation for testing."""
        return []

    def delete(self, ids):
        """Default delete implementation for testing."""
        pass

    def create_collection(self, name, dimension, metric):
        """Default create_collection implementation for testing."""
        pass


__all__ = ["BaseAdapter", "EmbeddingAdapter", "VectorDBAdapter", "DummyEmbeddingAdapter"]

# Ensure BaseAdapter has a default disconnect to avoid forcing subclasses in tests to implement it
BaseAdapter.disconnect = lambda self: None

class DummyEmbeddingAdapter(EmbeddingAdapter):
    """A dummy embedding adapter that returns fixed-size zero vectors for testing."""
    def connect(self):
        pass

    def disconnect(self):
        pass

    def embed(self, text: str):
        return [0.0] * 1536

    def embed_texts(self, texts):
        return [[0.0] * 1536 for _ in texts]
