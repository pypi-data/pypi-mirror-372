import faiss
import numpy as np
from typing import List, Dict, Optional, Any
from .vector_dbs_base import VectorDBAdapter


class FAISSAdapter(VectorDBAdapter):
    """FAISS vector database adapter."""

    def __init__(self, dimension: int = 768, index_type: str = "Flat"):
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.metadata_store = {}

    async def connect(self):
        if self.index_type == "Flat":
            self.index = faiss.IndexFlatL2(self.dimension)
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")

    async def create_collection(self, name: str, metadata: Optional[Dict] = None):
        # FAISS is in-memory; collections can be simulated via metadata
        self.metadata_store[name] = {"metadata": metadata or {}, "vectors": []}

    async def add_embeddings(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: List[str],
    ):
        if self.index is None:
            raise RuntimeError("FAISS index not initialized. Call connect() first.")

        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)

        for _id, meta in zip(ids, metadatas):
            self.metadata_store[collection_name]["vectors"].append({"id": _id, "metadata": meta})

    async def query(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 5,
    ) -> Any:
        if self.index is None:
            raise RuntimeError("FAISS index not initialized. Call connect() first.")

        query_vecs = np.array(query_embeddings).astype("float32")
        distances, indices = self.index.search(query_vecs, n_results)

        results = []
        for idx_list in indices:
            collection_vectors = self.metadata_store[collection_name]["vectors"]
            results.append([collection_vectors[i] for i in idx_list if i < len(collection_vectors)])

        return results
