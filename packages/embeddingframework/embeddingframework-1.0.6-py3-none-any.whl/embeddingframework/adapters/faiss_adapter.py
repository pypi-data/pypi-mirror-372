import faiss
import numpy as np
from typing import List, Dict, Optional, Any
from .base import VectorDBAdapter


class FAISSAdapter(VectorDBAdapter):
    def add_texts(self, texts, embeddings):
        """Default add_texts implementation for testing."""
        if not hasattr(self, "index") or self.index is None:
            raise RuntimeError("Index not initialized. Call connect or create index first.")
        import numpy as np
        import faiss
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        # Store texts in a simple list for retrieval simulation
        self.texts = getattr(self, "texts", []) + texts

    def add_texts(self, texts, embeddings):
        """Default add_texts implementation for testing."""
        if self.index is None:
            raise RuntimeError("FAISS index not initialized. Call connect() first.")
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadata_store.setdefault("default", {"vectors": []})
        start_index = len(self.metadata_store["default"]["vectors"])
        ids = []
        for i, txt in enumerate(texts, start=start_index):
            self.metadata_store["default"]["vectors"].append({"id": str(i), "metadata": {"text": txt}})
            ids.append(str(i))
        return ids
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
        return self.index

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
        return self.index

        for _id, meta in zip(ids, metadatas):
            self.metadata_store[collection_name]["vectors"].append({"id": _id, "metadata": meta})

    async def delete(self, ids):
        # FAISS does not support direct deletion; simulate by removing from metadata
        for collection in self.metadata_store.values():
            collection["vectors"] = [v for v in collection["vectors"] if v["id"] not in ids]
        print(f"Deleted vectors with IDs: {ids}")

    async def insert_embeddings(self, ids, embeddings, metadatas):
        if self.index is None:
            raise RuntimeError("FAISS index not initialized. Call connect() first.")
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadata_store.setdefault("default", {"vectors": []})
        for _id, meta in zip(ids, metadatas):
            self.metadata_store["default"]["vectors"].append({"id": _id, "metadata": meta})

    async def disconnect(self):
        self.index = None
        print("Disconnected from FAISS.")

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
        # Return both distances and indices for debugging if needed

        results = []
        for idx_list in indices:
            collection_vectors = self.metadata_store[collection_name]["vectors"]
            results.append([collection_vectors[i] for i in idx_list if i < len(collection_vectors)])

        return results
