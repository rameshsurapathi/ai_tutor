"""
rag_engine.py

Implements Retrieval-Augmented Generation (RAG) logic for IIT JEE textbook ingestion and retrieval.
- Supports adding new textbooks (PDF or text)
- Stores content in a vector database (ChromaDB)
- Retrieves relevant textbook chunks for a given query

Dependencies: chromadb, sentence-transformers, PyMuPDF (for PDF), tqdm
"""

import os
from pathlib import Path
from typing import List, Dict, Optional

# Import ChromaDB and SentenceTransformer for vector storage and embeddings
import chromadb
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

# Ensure tsqdm is installed for progress bars
from tqdm import tqdm

# Try to import PyMuPDF (fitz) for PDF text extraction
# If not available, raise an ImportError
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# Initialize embedding model (can use 'all-MiniLM-L6-v2' or similar)
# SentenceTransformer is used for generating text embeddings 
EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB client and collection
CHROMA_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db')
chroma_client = PersistentClient(path=CHROMA_DIR)


COLLECTION_NAME = 'NCERT_textbooks'
# Create or get the collection for storing textbook data
collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

# Function to extract text from a PDF file using PyMuPDF
def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """Extracts text from a PDF file, returns a list of page texts."""
    if fitz is None:
        raise ImportError("PyMuPDF (fitz) is required for PDF extraction.")
    doc = fitz.open(pdf_path)
    return [page.get_text() for page in doc]


# Function to chunk text into smaller pieces for better indexing
def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Splits text into chunks of ~chunk_size words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

# Function to add a PDF file or text file to the vector database
def add_pdf_file(file_path: str, book_name: str, source: str = "PDF"):
    """Ingests a textbook (PDF or .txt) and adds its content to the vector DB."""
    if file_path.lower().endswith('.pdf'):
        pages = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            pages = [f.read()]
    else:
        raise ValueError("Unsupported file type. Use PDF or TXT.")

    all_chunks = []
    for page_num, page_text in enumerate(pages):
        for chunk in chunk_text(page_text):
            all_chunks.append({
                'text': chunk,
                'book': book_name,
                'page': page_num + 1,
                'source': source
            })

    # Embed and add to ChromaDB
    for chunk in tqdm(all_chunks, desc=f"Indexing {book_name}"):
        embedding = EMBED_MODEL.encode(chunk['text']).tolist()
        collection.add(
            documents=[chunk['text']],
            embeddings=[embedding],
            metadatas=[{
                'book': chunk['book'],
                'page': chunk['page'],
                'source': chunk['source']
            }],
            ids=[f"{book_name}_{chunk['page']}_{hash(chunk['text'])}"]
        )

# Function to retrieve relevant textbook chunks for a given query
def retrieve_relevant_chunks(query: str, top_k: int = 5) -> List[Dict]:
    """Retrieves top-k relevant textbook chunks for a query."""
    query_emb = EMBED_MODEL.encode(query).tolist()
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)
    # Format: [{'text': ..., 'book': ..., 'page': ..., ...}, ...]
    chunks = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        chunks.append({
            'text': doc,
            'book': meta['book'],
            'page': meta['page'],
            'source': meta['source']
        })
    return chunks

# function to add pdf textbooks from a directory
def add_textbook(dir_path:str,book_name:str):

    pdf_dir = Path(dir_path)
    if not pdf_dir.exists():
        raise FileNotFoundError(f"Directory {pdf_dir} does not exist.")

    # Add all PDF textbooks in the specified directory
    for pdf_path in pdf_dir.glob("*.pdf"):
        book_name = pdf_path.stem
        print(f"Adding {pdf_path} as {book_name}")
        add_pdf_file(str(pdf_path), book_name)
    
if __name__=="__main__":

    pass
    #add_textbook('/Users/rameshsurapathi/Downloads/maths_book/', 'NCERT Maths 10th class All Chapters')
    #print(retrieve_relevant_chunks('Give the names of all the chapters of NCERT Maths 10th class'))