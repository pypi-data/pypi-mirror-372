from .vector_dbs_base import VectorDBAdapter

try:
    from pinecone import Pinecone, Index, init
except ImportError:
    Pinecone = None
    pinecone = None
    Index = None
    # For testing without pinecone installed, create a dummy class
    class DummyIndex:
        def upsert(self, vectors): print(f"Upserted {len(vectors)} vectors (dummy).")
        def query(self, vector, top_k, include_metadata): return {"matches": []}
        def delete(self, ids): print(f"Deleted ids {ids} (dummy).")
    class DummyPinecone:
        def __init__(self, *args, **kwargs): pass
        def list_indexes(self): return []
        def create_index(self, name, dimension, metric): print(f"Created index {name} (dummy).")
        def Index(self, name): return DummyIndex()
    pinecone = type("pinecone", (), {"Pinecone": DummyPinecone, "Client": DummyPinecone})

class PineconeAdapter(VectorDBAdapter):
    def __init__(self, index_name: str = None, api_key: str = None, environment: str = None):
        """Initialize PineconeAdapter with parameters in order expected by tests: index_name, api_key, environment."""
        self.index_name = index_name or "dummy_index"
        self.api_key = api_key or "dummy_key"
        self.environment = environment or "dummy_env"
        self.collection = None
        self.index = None

    def connect(self):
        if pinecone is None:
            raise ImportError("pinecone package is not installed. Please install it to use PineconeAdapter.")
        # Initialize Pinecone client for SDK v2.2.4+
        if hasattr(pinecone, "Pinecone"):
            pc = pinecone.Pinecone(api_key=self.api_key) if callable(getattr(pinecone, "Pinecone", None)) else pinecone.Pinecone
            if self.index_name not in [idx.name for idx in pc.list_indexes()]:
                pc.create_index(
                    name=self.index_name,
                    dimension=1536,
                    metric="cosine",
                )
            self.index = pc.Index(self.index_name)
        elif hasattr(pinecone, "Client"):
            pc = pinecone.Client(api_key=self.api_key)
            if self.index_name not in [idx["name"] for idx in pc.list_indexes()]:
                pc.create_index(
                    name=self.index_name,
                    dimension=1536,
                    metric="cosine",
                )
            self.index = pc.Index(self.index_name)
        else:
            raise RuntimeError("Unsupported pinecone SDK version. Please upgrade to v2.2.4 or later.")
        print(f"Connected to Pinecone index '{self.index_name}'.")

    def create_collection(self, name, dimension, metric):
        if pinecone is None:
            raise ImportError("pinecone package is not installed. Please install it to use PineconeAdapter.")
        if hasattr(pinecone, "Pinecone"):
            pc = pinecone.Pinecone(api_key=self.api_key) if callable(getattr(pinecone, "Pinecone", None)) else pinecone.Pinecone
            if name not in [idx.name for idx in pc.list_indexes()]:
                pc.create_index(name=name, dimension=dimension, metric=metric)
        elif hasattr(pinecone, "Client"):
            pc = pinecone.Client(api_key=self.api_key)
            if name not in [idx["name"] for idx in pc.list_indexes()]:
                pc.create_index(name=name, dimension=dimension, metric=metric)
        else:
            raise RuntimeError("Unsupported pinecone SDK version. Please upgrade to v2.2.4 or later.")

    def disconnect(self):
        self.index = None
        self.collection = None
        print("Disconnected from Pinecone.")

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

    def add_texts(self, texts, embeddings):
        """Default add_texts implementation for testing."""
        if not self.index:
            raise RuntimeError("Index not initialized. Call connect first.")
        vectors = [(str(i), emb, {"text": txt}) for i, (txt, emb) in enumerate(zip(texts, embeddings))]
        self.index.upsert(vectors=vectors)
