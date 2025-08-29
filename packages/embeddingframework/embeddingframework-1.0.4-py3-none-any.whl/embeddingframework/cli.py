import argparse
import asyncio
import logging
from embeddingframework.adapters.providers import OpenAIEmbeddingAdapter, HuggingFaceEmbeddingAdapter
from embeddingframework.adapters.vector_dbs import ChromaDBAdapter, FAISSAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


async def ingest(args):
    if args.provider == "openai":
        provider = OpenAIEmbeddingAdapter(api_key=args.api_key)
    elif args.provider == "huggingface":
        provider = HuggingFaceEmbeddingAdapter(model_name=args.model_name)
    else:
        raise ValueError("Unsupported provider")

    if args.db == "chromadb":
        db = ChromaDBAdapter()
    elif args.db == "faiss":
        db = FAISSAdapter(dimension=args.dimension)
    else:
        raise ValueError("Unsupported vector DB")

    await db.connect()
    await db.create_collection(args.collection)

    embedding = provider.embed(args.text)
    await db.add_embeddings(args.collection, [embedding], [{"text": args.text}], [args.id])
    logging.info("Ingestion complete.")


async def query(args):
    if args.provider == "openai":
        provider = OpenAIEmbeddingAdapter(api_key=args.api_key)
    elif args.provider == "huggingface":
        provider = HuggingFaceEmbeddingAdapter(model_name=args.model_name)
    else:
        raise ValueError("Unsupported provider")

    if args.db == "chromadb":
        db = ChromaDBAdapter()
    elif args.db == "faiss":
        db = FAISSAdapter(dimension=args.dimension)
    else:
        raise ValueError("Unsupported vector DB")

    await db.connect()
    embedding = provider.embed(args.text)
    results = await db.query(args.collection, [embedding], n_results=args.top_k)
    logging.info(f"Query results: {results}")


def main():
    parser = argparse.ArgumentParser(description="EmbeddingFramework CLI")
    subparsers = parser.add_subparsers(dest="command")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest text into vector DB")
    ingest_parser.add_argument("--provider", required=True, choices=["openai", "huggingface"])
    ingest_parser.add_argument("--api_key", help="API key for provider")
    ingest_parser.add_argument("--model_name", help="HuggingFace model name")
    ingest_parser.add_argument("--db", required=True, choices=["chromadb", "faiss"])
    ingest_parser.add_argument("--dimension", type=int, default=768)
    ingest_parser.add_argument("--collection", required=True)
    ingest_parser.add_argument("--text", required=True)
    ingest_parser.add_argument("--id", required=True)
    ingest_parser.set_defaults(func=ingest)

    query_parser = subparsers.add_parser("query", help="Query vector DB")
    query_parser.add_argument("--provider", required=True, choices=["openai", "huggingface"])
    query_parser.add_argument("--api_key", help="API key for provider")
    query_parser.add_argument("--model_name", help="HuggingFace model name")
    query_parser.add_argument("--db", required=True, choices=["chromadb", "faiss"])
    query_parser.add_argument("--dimension", type=int, default=768)
    query_parser.add_argument("--collection", required=True)
    query_parser.add_argument("--text", required=True)
    query_parser.add_argument("--top_k", type=int, default=5)
    query_parser.set_defaults(func=query)

    args = parser.parse_args()
    if hasattr(args, "func"):
        asyncio.run(args.func(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
