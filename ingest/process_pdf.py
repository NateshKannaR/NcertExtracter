import sys
import uuid
import fitz  # PyMuPDF
from embeddings import upsert_chunks

# --- Helper Function for Chunking ---
def chunk_text(text: str, page_no: int, title: str, max_tokens: int = 400, overlap: int = 80):
    """
    Splits a long text into smaller chunks with a specified overlap.
    Approximates tokens by splitting on whitespace.
    """
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + max_tokens]
        chunk_text_content = ' '.join(chunk_words)
        chunk_id = str(uuid.uuid4())
        metas = {
            'title': title,
            'page': page_no,
            'source': title or 'uploaded_pdf'
        }
        chunks.append({'id': chunk_id, 'text': chunk_text_content, 'meta': metas})
        i += max_tokens - overlap
    return chunks

# --- Main Processing Function ---
def process(path: str, title: str = ''):
    """
    Opens a PDF, extracts text from each page, chunks it, and upserts it
    into the vector database via the upsert_chunks function.
    """
    if not title:
        title = path # Use the file path as a default title
        
    print(f"Starting processing for: {title}")
    doc = fitz.open(path)
    all_chunks = []
    for page_no, page in enumerate(doc, start=1):
        text = page.get_text("text")
        if not text.strip():
            continue
        page_chunks = chunk_text(text, page_no, title)
        all_chunks.extend(page_chunks)
    
    # Upsert all chunks from the document at once
    if all_chunks:
        upsert_chunks(all_chunks)
        print(f"Indexed {len(all_chunks)} chunks from {path}")
    else:
        print(f"No text found in {path}")

# --- Standalone Script Execution ---
if __name__ == '__main__':
    """
    Allows this script to be run from the command line.
    Usage: python process_pdf.py /path/to/file.pdf [title]
    NOTE: Run this script from the `backend/app` directory to ensure
    imports and database paths work correctly.
    """
    if len(sys.argv) < 2:
        print('Usage: python process_pdf.py /path/to/file.pdf [optional_title]')
        sys.exit(1)
        
    file_path = sys.argv[1]
    file_title = sys.argv[2] if len(sys.argv) > 2 else ''
    process(file_path, file_title)
