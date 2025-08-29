from .base import VectorDBAdapter
import chromadb
from chromadb.config import Settings


class ChromaDBAdapter(VectorDBAdapter):
    def add_texts(self, texts, embeddings):
        """Default add_texts implementation for testing."""
        if not getattr(self, "collection", None):
            if not getattr(self, "client", None):
                self.connect()
            self.create_collection("default")
        ids = [str(i) for i in range(len(texts))]
        metadatas = [{"text": t} for t in texts]
        self.collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)
        print(f"Added {len(texts)} texts to ChromaDB collection.")
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None

    def connect(self):
        self.client = chromadb.Client(Settings(persist_directory=self.persist_directory))
        print(f"Connected to ChromaDB at {self.persist_directory}")

    def create_collection(self, name: str):
        self.collection = self.client.get_or_create_collection(name=name)
        print(f"ChromaDB collection '{name}' ready.")

    def insert_embeddings(self, ids, embeddings, metadatas):
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call create_collection first.")
        self.collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)

    def query(self, query_embeddings, n_results=5):
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call create_collection first.")
        return self.collection.query(query_embeddings=query_embeddings, n_results=n_results)

    def delete(self, ids):
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call create_collection first.")
        self.collection.delete(ids=ids)

    def disconnect(self):
        self.client = None
        self.collection = None
        print("Disconnected from ChromaDB.")
