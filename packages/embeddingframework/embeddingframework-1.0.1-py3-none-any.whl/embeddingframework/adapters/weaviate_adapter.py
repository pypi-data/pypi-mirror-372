from .vector_dbs_base import VectorDBAdapter
import weaviate


class WeaviateAdapter(VectorDBAdapter):
    def __init__(self, url: str, api_key: str = None):
        self.url = url
        self.api_key = api_key
        self.client = None

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
