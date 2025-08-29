<h1 align="center">🚀 EmbeddingFramework</h1>

<p align="center">
  <b>Modular • Extensible • Production-Ready</b><br>
  A Python framework for embeddings, vector databases, and cloud storage providers.
</p>

<p align="center">
  <a href="https://github.com/isathish/embeddingframework/actions"><img src="https://img.shields.io/github/actions/workflow/status/isathish/embeddingframework/python-package.yml?branch=main" alt="Build Status"></a>
  <a href="https://pypi.org/project/embeddingframework/"><img src="https://img.shields.io/pypi/v/embeddingframework" alt="PyPI Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

---

A **modular, extensible, and production-ready** Python framework for working with embeddings, vector databases, and cloud storage providers.  
Designed for **AI, NLP, and semantic search** applications, EmbeddingFramework provides a unified API to process, store, and query embeddings across multiple backends.

---

## ✨ Features

### 🔹 **Multi-Vector Database Support**
- **ChromaDB** – Local and persistent vector storage.
- **Milvus** – High-performance distributed vector database.
- **Pinecone** – Fully managed vector database service.
- **Weaviate** – Open-source vector search engine.

### 🔹 **Cloud Storage Integrations**
- **AWS S3** – Store and retrieve embeddings or documents.
- **Google Cloud Storage (GCS)** – Scalable object storage.
- **Azure Blob Storage** – Enterprise-grade cloud storage.

### 🔹 **Embedding Providers**
- **OpenAI Embeddings** – State-of-the-art embedding generation.
- Easily extendable to other providers.

### 🔹 **File Processing & Preprocessing**
- Automatic file type detection.
- Text extraction from multiple formats.
- Preprocessing utilities for cleaning and normalizing text.
- Intelligent text splitting for optimal embedding performance.

### 🔹 **Utilities**
- Retry logic for robust API calls.
- File utilities for safe and efficient I/O.
- Modular architecture for easy extension.

---

## 📦 Installation & Setup

```bash
# Basic installation
pip install embeddingframework

# With development dependencies
pip install embeddingframework[dev]
```

---

## ⚡ Quick Start Example

```python
from embeddingframework.adapters.openai_embedding_adapter import OpenAIEmbeddingAdapter
from embeddingframework.adapters.vector_dbs import ChromaDBAdapter

# Initialize embedding provider
embedding_provider = OpenAIEmbeddingAdapter(api_key="YOUR_OPENAI_API_KEY")

# Initialize vector database
vector_db = ChromaDBAdapter(persist_directory="./chroma_store")

# Generate embeddings
embeddings = embedding_provider.embed_texts(["Hello world", "EmbeddingFramework is awesome!"])

# Store embeddings
vector_db.add_texts(["Hello world", "EmbeddingFramework is awesome!"], embeddings)
```

---

## 📂 Project Structure

```
embeddingframework/
│
├── adapters/                # Vector DB & storage adapters
│   ├── base.py
│   ├── chromadb_adapter.py
│   ├── milvus_adapter.py
│   ├── pinecone_adapter.py
│   ├── weaviate_adapter.py
│   ├── storage/             # Cloud storage adapters
│
├── processors/              # File processing logic
├── utils/                    # Helper utilities
└── tests/                    # Test suite
```

---

## 🧪 Testing

```bash
pytest --maxfail=1 --disable-warnings -q
```

With coverage:

```bash
pytest --cov=embeddingframework --cov-report=term-missing
```

---

## 🔄 CI/CD

This project includes a **GitHub Actions** workflow (`.github/workflows/python-package.yml`) for:
- Automated testing with coverage.
- Version bumping & changelog generation.
- PyPI publishing.
- GitHub release creation.

---

## 📜 License
<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
</p>

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing
<p align="center">
  Contributions, issues, and feature requests are welcome!<br>
  Feel free to check the <a href="https://github.com/isathish/embeddingframework/issues">issues page</a>.
</p>

1. Fork the repository.
2. Create a new branch (`feature/my-feature`).
3. Commit your changes.
4. Push to your branch.
5. Open a Pull Request.

---

## 🌟 Why EmbeddingFramework?

- **Unified API** – Work with multiple vector DBs and storage providers seamlessly.
- **Extensible** – Add new adapters with minimal effort.
- **Production-Ready** – Built with scalability and reliability in mind.
- **Developer-Friendly** – Clean, modular, and well-documented codebase.
