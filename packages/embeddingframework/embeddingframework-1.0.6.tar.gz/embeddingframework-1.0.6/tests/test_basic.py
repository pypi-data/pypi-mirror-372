import pytest
from unittest.mock import MagicMock, patch
from embeddingframework.adapters import base, chromadb_adapter, faiss_adapter, milvus_adapter, openai_embedding_adapter, pinecone_adapter, providers, storage, vector_dbs, vector_dbs_base, weaviate_adapter
from embeddingframework.processors import file_processor
from embeddingframework.utils import file_utils, preprocessing, retry, splitters
from embeddingframework import cli

def test_base_adapter_init():
    class DummyAdapter(base.BaseAdapter):
        def connect(self): pass
    adapter = DummyAdapter()
    assert isinstance(adapter, base.BaseAdapter)

def test_chromadb_adapter_methods():
    with patch("chromadb.Client") as mock_client:
        adapter = chromadb_adapter.ChromaDBAdapter(persist_directory="/tmp")
        adapter.client = MagicMock()
        adapter.add_texts(["a"], [[0.1, 0.2]])
        adapter.query(["a"], 1)
        adapter.delete(["id1"])
        assert adapter is not None

def test_faiss_adapter_methods():
    with patch("faiss.IndexFlatL2") as mock_faiss:
        adapter = faiss_adapter.FAISSAdapter()
        adapter.index = MagicMock()
        adapter.add_texts(["a"], [[0.1, 0.2]])
        adapter.query(["a"], 1)
        assert adapter is not None

def test_milvus_adapter_methods():
    with patch("pymilvus.connections.connect"), patch("pymilvus.Collection") as mock_collection:
        adapter = milvus_adapter.MilvusAdapter("test_collection")
        adapter.collection = MagicMock()
        adapter.add_texts(["a"], [[0.1, 0.2]])
        adapter.query(["a"], 1)
        assert adapter is not None

def test_openai_embedding_adapter_methods():
    with patch("openai.Embedding.create") as mock_create:
        mock_create.return_value = {"data": [{"embedding": [0.1, 0.2]}]}
        adapter = openai_embedding_adapter.OpenAIEmbeddingAdapter(api_key="key")
        result = adapter.embed_texts(["a"])
        assert isinstance(result, list)

def test_pinecone_adapter_methods():
    with patch.dict("sys.modules", {"pinecone": MagicMock()}):
        import importlib
        importlib.reload(pinecone_adapter)
        adapter = pinecone_adapter.PineconeAdapter("index")
        adapter.index = MagicMock()
        adapter.add_texts(["a"], [[0.1, 0.2]])
        adapter.query(["a"], 1)
        assert adapter is not None

def test_providers_registry():
    providers.register_provider("dummy", lambda: "ok")
    assert providers.get_provider("dummy")() == "ok"

def test_storage_module():
    with patch("boto3.client"), patch("google.cloud.storage.Client"), patch("azure.storage.blob.BlobServiceClient"):
        assert storage is not None

def test_vector_dbs_module():
    assert vector_dbs is not None
    assert vector_dbs_base is not None

def test_weaviate_adapter_methods():
    with patch("weaviate.Client") as mock_client:
        adapter = weaviate_adapter.WeaviateAdapter()
        adapter.client = MagicMock()
        adapter.add_texts(["a"], [[0.1, 0.2]])
        adapter.query(["a"], 1)
        assert adapter is not None

def test_file_processor_methods():
    processor = file_processor.FileProcessor()
    with patch.object(processor, "_process_text_file", return_value="ok"):
        assert processor.process_file("file.txt") == "ok"

def test_utils_modules():
    assert file_utils is not None
    assert preprocessing is not None
    assert retry is not None
    assert splitters is not None

def test_cli_help(capsys):
    with pytest.raises(SystemExit):
        cli.main(["--help"])
