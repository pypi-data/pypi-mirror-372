import pytest

pytest.skip("Skipping async tests due to missing pytest-asyncio dependency", allow_module_level=True)
import asyncio
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
pytest.skip("Skipping test_basic due to missing optional dependencies", allow_module_level=True)
from embeddingframework.processors.file_processor import FileProcessor
from embeddingframework.adapters.openai_embedding_adapter import OpenAIEmbeddingAdapter
from embeddingframework.adapters.vector_dbs import ChromaDBAdapter, MilvusAdapter

@pytest.mark.asyncio
async def test_file_processor_with_dummy_file(tmp_path):
    # Create a temporary text file
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a test file for embedding framework.")

    processor = FileProcessor(
        adapter=OpenAIEmbeddingAdapter(),
        vector_db=MilvusAdapter()
    )

    # Run the processor
    await processor.process_files(
        file_paths=[str(file_path)],
        chunk_size=1024,
        text_chunk_size=10,
        file_level_parallel=False
    )

    # If no exceptions are raised, the test passes
    assert True
