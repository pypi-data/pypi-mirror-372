from abc import ABC, abstractmethod
from typing import List, Any, Optional


class VectorDBAdapter(ABC):
    """
    Base class for all Vector Database Adapters.
    Defines the interface that all adapters must implement.
    """

    @abstractmethod
    async def connect(self, **kwargs) -> None:
        """
        Connect to the vector database.
        """
        pass

    @abstractmethod
    async def create_collection(self, name: str, metadata: Optional[dict] = None) -> None:
        """
        Create a new collection in the vector database.
        """
        pass

    @abstractmethod
    async def insert_embeddings(self, collection_name: str, embeddings: List[List[float]], metadatas: List[dict], ids: Optional[List[str]] = None) -> None:
        """
        Insert embeddings into the specified collection.
        """
        pass

    @abstractmethod
    async def query(self, collection_name: str, query_embedding: List[float], top_k: int = 5) -> List[Any]:
        """
        Query the vector database for the most similar embeddings.
        """
        pass

    @abstractmethod
    async def delete(self, collection_name: str, ids: List[str]) -> None:
        """
        Delete embeddings from the specified collection by IDs.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from the vector database.
        """
        pass
