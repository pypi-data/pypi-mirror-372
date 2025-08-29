from typing import List, Protocol

class EmbeddingAdapter(Protocol):
    """Protocol for embedding model adapters."""
    def embed(self, text: str) -> List[float]:
        ...

class DummyEmbeddingAdapter:
    """A dummy adapter for testing without a real embedding model."""
    def embed(self, text: str) -> List[float]:
        return [float(len(text))] * 10
