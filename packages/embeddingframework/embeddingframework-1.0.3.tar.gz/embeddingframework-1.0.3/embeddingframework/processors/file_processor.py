import os
import asyncio
import mimetypes
import aiofiles
import logging
from embeddingframework.utils.retry import retry_on_exception
import concurrent.futures
from typing import List, Optional
from embeddingframework.adapters.base import EmbeddingAdapter, DummyEmbeddingAdapter
from embeddingframework.utils.splitters import split_file_by_type
from embeddingframework.utils.preprocessing import preprocess_chunks
from embeddingframework.adapters.vector_dbs import VectorDBAdapter, ChromaDBAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from embeddingframework.processors.file_processor import FileProcessor as BaseFileProcessor
else:
    BaseFileProcessor = object

class FileProcessor:
    def __init__(self, collection=None, adapter: Optional[EmbeddingAdapter] = None, vector_db: Optional[VectorDBAdapter] = None):
        self.collection = collection
        self.adapter = adapter or DummyEmbeddingAdapter()
        self.vector_db = vector_db

    async def stream_file(self, file_path: str, chunk_size: int, bandwidth_limit: Optional[int] = None):
        """
        Stream file asynchronously in chunks.
        - chunk_size: size of each chunk in bytes
        - bandwidth_limit: max bytes per second to avoid network congestion
        """
        async with aiofiles.open(file_path, mode='rb') as f:
            while True:
                data = await f.read(chunk_size)
                if not data:
                    break
                yield data
                if bandwidth_limit:
                    await asyncio.sleep(len(data) / bandwidth_limit)

    def split_text(self, text: str, max_length: int) -> List[str]:
        """Split text into smaller chunks based on max_length."""
        return [text[i:i+max_length] for i in range(0, len(text), max_length)]

    def merge_chunks(self, chunks: List[str], target_length: int) -> List[str]:
        """Merge smaller chunks into larger ones if needed."""
        merged = []
        buffer = ""
        for chunk in chunks:
            if len(buffer) + len(chunk) <= target_length:
                buffer += chunk
            else:
                merged.append(buffer)
                buffer = chunk
        if buffer:
            merged.append(buffer)
        return merged

    def quality_filter(self, chunks: List[str], min_length: int = 20) -> List[str]:
        """Filter out chunks that are too small or low quality."""
        return [chunk for chunk in chunks if len(chunk.strip()) >= min_length]

    @retry_on_exception(max_tries=5)
    async def store_chunk(self, chunk: str, metadata: dict, chunk_id: str):
        """Store a single chunk in ChromaDB with retry on failure."""
        embedding = self.adapter.embed(chunk)
        if self.collection:
            self.collection.add(documents=[chunk], embeddings=[embedding], metadatas=[metadata], ids=[chunk_id])
        elif self.vector_db:
            await self.vector_db.add_embeddings(collection_name=metadata.get("collection", "default"), embeddings=[embedding], metadatas=[metadata], ids=[chunk_id])
        else:
            raise ValueError("No storage backend configured for storing embeddings.")

    async def process_file(self, file_path: str, chunk_size: int, text_chunk_size: int, merge_target_size: Optional[int] = None, parallel: bool = True, min_quality_length: int = 20, bandwidth_limit: Optional[int] = None, semaphore: Optional[asyncio.Semaphore] = None):
        """Process a file: stream, split, merge, filter, embed, and store with optional concurrency limits."""
        if semaphore:
            async with semaphore:
                return await self._process_file_internal(file_path, chunk_size, text_chunk_size, merge_target_size, parallel, min_quality_length, bandwidth_limit)
        else:
            return await self._process_file_internal(file_path, chunk_size, text_chunk_size, merge_target_size, parallel, min_quality_length, bandwidth_limit)

    async def _process_file_internal(self, file_path: str, chunk_size: int, text_chunk_size: int, merge_target_size: Optional[int], parallel: bool, min_quality_length: int, bandwidth_limit: Optional[int]):
        mime_type, _ = mimetypes.guess_type(file_path)
        file_name = os.path.basename(file_path)

        logging.info(f"Processing file: {file_name}")

        # Use custom splitters for supported file types
        try:
            text_chunks = split_file_by_type(file_path, text_chunk_size)
        except Exception as e:
            logging.warning(f"Custom splitter failed for {file_name}, falling back to binary streaming: {e}")
            text_chunks = []
            async for binary_chunk in self.stream_file(file_path, chunk_size, bandwidth_limit):
                try:
                    text = binary_chunk.decode('utf-8', errors='ignore')
                    text_chunks.extend(self.split_text(text, text_chunk_size))
                except Exception as e:
                    logging.warning(f"Skipping binary chunk due to decode error: {e}")

        if merge_target_size:
            text_chunks = self.merge_chunks(text_chunks, merge_target_size)

        text_chunks = self.quality_filter(text_chunks, min_quality_length)

        # Preprocess chunks (cleaning, normalization, stopword removal)
        try:
            text_chunks = preprocess_chunks(text_chunks)
        except Exception as e:
            logging.warning(f"Preprocessing failed for {file_name}: {e}")

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            tasks = []
            for idx, chunk in enumerate(text_chunks):
                metadata = {"file_name": file_name, "chunk_index": idx, "mime_type": mime_type}
                chunk_id = f"{file_name}_{idx}"
                if parallel:
                    tasks.append(self.store_chunk(chunk, metadata, chunk_id))
                else:
                    await self.store_chunk(chunk, metadata, chunk_id)
            if parallel:
                await asyncio.gather(*tasks)

        logging.info(f"Completed processing {file_name} with {len(text_chunks)} quality chunks.")

    async def process_files(self, file_paths: List[str], chunk_size: int, text_chunk_size: int, merge_target_size: Optional[int] = None, parallel: bool = True, min_quality_length: int = 20, file_level_parallel: bool = True, bandwidth_limit: Optional[int] = None, max_concurrent_files: Optional[int] = None):
        """
        Process multiple files with flexible parallelism and bandwidth control:
        - file_level_parallel: process multiple files concurrently
        - parallel: process chunks within each file concurrently
        - bandwidth_limit: max bytes per second to avoid packet loss
        - max_concurrent_files: limit number of files processed at the same time
        """
        semaphore = asyncio.Semaphore(max_concurrent_files) if max_concurrent_files else None
        if file_level_parallel:
            await asyncio.gather(*(self.process_file(fp, chunk_size, text_chunk_size, merge_target_size, parallel, min_quality_length, bandwidth_limit, semaphore) for fp in file_paths))
        else:
            for fp in file_paths:
                await self.process_file(fp, chunk_size, text_chunk_size, merge_target_size, parallel, min_quality_length, bandwidth_limit, semaphore)
