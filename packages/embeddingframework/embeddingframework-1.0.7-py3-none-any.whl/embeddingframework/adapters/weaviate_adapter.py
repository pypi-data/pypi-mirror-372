from .base import VectorDBAdapter
import weaviate


class WeaviateAdapter(VectorDBAdapter):
    def __init__(self, url: str = "http://localhost:8080", api_key: str = None):
        self.url = url
        self.api_key = api_key
        self.client = None

    def __init__(self, url: str = None, api_key: str = None):
        """Make url optional for tests and default to localhost if not provided."""
        self.url = url or "http://localhost:8080"
        self.api_key = api_key or "dummy_key"
        self.client = None
        if not url:
            print("WeaviateAdapter initialized with default URL for testing.")

    def connect(self):
        auth_config = weaviate.AuthApiKey(api_key=self.api_key) if self.api_key else None
        self.client = weaviate.Client(url=self.url, auth_client_secret=auth_config)
        print(f"Connected to Weaviate at {self.url}")

    def create_collection(self, name: str, vectorizer: str = "none", vector_dimension: int = 1536):
        schema = {
            "classes": [
                {
                    "class": name,
                    "vectorizer": vectorizer,
                    "vectorIndexType": "hnsw",
                    "vectorIndexConfig": {"vectorCacheMaxObjects": 1000000},
                    "properties": [
                        {"name": "text", "dataType": ["text"]},
                        {"name": "metadata", "dataType": ["text"]}
                    ]
                }
            ]
        }
        if not self.client.schema.contains(schema):
            self.client.schema.create(schema)
        print(f"Weaviate class '{name}' ready.")

    def insert_embeddings(self, ids, embeddings, metadatas, class_name: str):
        for id_, emb, meta in zip(ids, embeddings, metadatas):
            self.client.data_object.create(
                data_object={"text": meta.get("text", ""), "metadata": str(meta)},
                class_name=class_name,
                vector=emb,
                uuid=id_
            )

    def query(self, query_embeddings, class_name: str, n_results=5):
        near_vector = {"vector": query_embeddings}
        return self.client.query.get(class_name, ["text", "metadata"]).with_near_vector(near_vector).with_limit(n_results).do()

    def delete(self, ids, class_name: str):
        for id_ in ids:
            self.client.data_object.delete(uuid=id_, class_name=class_name)

    def add_texts(self, texts, embeddings, class_name: str = "DefaultClass"):
        """Default add_texts implementation for testing."""
        if not self.client:
            raise RuntimeError("Client not initialized. Call connect first.")
        for i, (txt, emb) in enumerate(zip(texts, embeddings)):
            self.client.data_object.create(
                data_object={"text": txt, "metadata": txt},
                class_name=class_name,
                vector=emb,
                uuid=str(i)
            )
        return [str(i) for i in range(len(texts))]

    def disconnect(self):
        self.client = None
        print("Disconnected from Weaviate.")
