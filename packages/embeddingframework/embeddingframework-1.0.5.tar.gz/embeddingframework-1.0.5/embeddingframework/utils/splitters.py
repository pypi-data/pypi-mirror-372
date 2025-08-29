import logging
from typing import List
from PyPDF2 import PdfReader
import docx
import csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def split_text_file(file_path: str, chunk_size: int) -> List[str]:
    """Split plain text files into chunks."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def split_pdf_file(file_path: str, chunk_size: int) -> List[str]:
    """Extract text from PDF and split into chunks."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def split_docx_file(file_path: str, chunk_size: int) -> List[str]:
    """Extract text from DOCX and split into chunks."""
    document = docx.Document(file_path)
    text = "\n".join([para.text for para in document.paragraphs])
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def split_csv_file(file_path: str, chunk_size: int) -> List[str]:
    """Read CSV and split rows into chunks of text."""
    rows = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(", ".join(row))
    text = "\n".join(rows)
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def split_file_by_type(file_path: str, chunk_size: int) -> List[str]:
    """Determine file type and use appropriate splitting method."""
    if file_path.lower().endswith('.pdf'):
        return split_pdf_file(file_path, chunk_size)
    elif file_path.lower().endswith('.docx'):
        return split_docx_file(file_path, chunk_size)
    elif file_path.lower().endswith('.csv'):
        return split_csv_file(file_path, chunk_size)
    else:
        return split_text_file(file_path, chunk_size)
