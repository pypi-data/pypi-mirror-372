import re
import logging
from typing import List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def clean_text(text: str) -> str:
    """Basic text cleaning: remove extra spaces, normalize whitespace."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_stopwords(text: str, stopwords: List[str]) -> str:
    """Remove stopwords from text."""
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stopwords]
    return ' '.join(filtered_words)

def normalize_text(text: str) -> str:
    """Lowercase and strip text."""
    return text.lower().strip()

def preprocess_chunks(chunks: List[str], stopwords: List[str] = None, normalize: bool = True, clean: bool = True) -> List[str]:
    """Apply preprocessing steps to a list of text chunks."""
    processed = []
    for chunk in chunks:
        if clean:
            chunk = clean_text(chunk)
        if normalize:
            chunk = normalize_text(chunk)
        if stopwords:
            chunk = remove_stopwords(chunk, stopwords)
        processed.append(chunk)
    return processed
