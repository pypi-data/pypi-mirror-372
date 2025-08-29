from .chromadb_adapter import ChromaDBAdapter
import importlib

PineconeAdapter = None
WeaviateAdapter = None

try:
    if importlib.util.find_spec("pinecone") is not None:
        from .pinecone_adapter import PineconeAdapter
except (ImportError, AttributeError):
    PineconeAdapter = None

if importlib.util.find_spec("weaviate") is not None:
    try:
        from .weaviate_adapter import WeaviateAdapter
    except ImportError:
        WeaviateAdapter = None
from .milvus_adapter import MilvusAdapter
from .faiss_adapter import FAISSAdapter
import abc
from typing import List, Any, Dict, Optional


class VectorDBAdapter(abc.ABC):
    """Abstract base class for vector database adapters."""

    @abc.abstractmethod
    async def connect(self):
        pass

    @abc.abstractmethod
    async def create_collection(self, name: str, metadata: Optional[Dict] = None):
        pass

    @abc.abstractmethod
    async def add_embeddings(self, collection_name: str, embeddings: List[List[float]], metadatas: List[Dict], ids: List[str]):
        pass

    @abc.abstractmethod
    async def query(self, collection_name: str, query_embeddings: List[List[float]], n_results: int = 5) -> Any:
        pass
