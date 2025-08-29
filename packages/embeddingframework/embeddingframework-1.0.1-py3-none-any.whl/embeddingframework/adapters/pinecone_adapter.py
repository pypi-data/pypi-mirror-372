# Import both the pinecone namespace and specific classes for compatibility
from .vector_dbs_base import VectorDBAdapter
import pinecone
from pinecone import Index, init


class PineconeAdapter(VectorDBAdapter):
    def __init__(self, api_key: str, environment: str, index_name: str):
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.index = None

    def connect(self):
        init(api_key=self.api_key, environment=self.environment)
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(self.index_name, dimension=1536, metric="cosine")
        self.index = Index(self.index_name)
        print(f"Connected to Pinecone index '{self.index_name}' in environment '{self.environment}'.")

    def insert_embeddings(self, ids, embeddings, metadatas):
        if not self.index:
            raise RuntimeError("Index not initialized. Call connect first.")
        vectors = [(id_, emb, meta) for id_, emb, meta in zip(ids, embeddings, metadatas)]
        self.index.upsert(vectors=vectors)

    def query(self, query_embeddings, n_results=5):
        if not self.index:
            raise RuntimeError("Index not initialized. Call connect first.")
        return self.index.query(vector=query_embeddings, top_k=n_results, include_metadata=True)

    def delete(self, ids):
        if not self.index:
            raise RuntimeError("Index not initialized. Call connect first.")
        self.index.delete(ids=ids)
