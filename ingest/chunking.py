# chunker.py
import uuid
from typing import List, Dict

def chunk_text(
    text: str,
    page_no: int,
    title: str,
    max_tokens: int = 400,
    overlap: int = 80
) -> List[Dict]:
    """
    Splits text into chunks with overlap. Approximates tokens with words.

    Args:
        text (str): The full text to chunk.
        page_no (int): Page number for metadata.
        title (str): Title of the source.
        max_tokens (int): Max words per chunk.
        overlap (int): Number of words to overlap between chunks.

    Returns:
        List[Dict]: List of chunks with id, text, and metadata.
    """
    words = text.split()
    chunks = []
    i = 0

    while i < len(words):
        chunk_words = words[i:i+max_tokens]
        chunk_text_str = ' '.join(chunk_words)
        chunk_id = str(uuid.uuid4())
        metas = {
            'title': title,
            'page': page_no,
            'source': title or 'uploaded_pdf'
        }
        chunks.append({'id': chunk_id, 'text': chunk_text_str, 'meta': metas})
        i += max_tokens - overlap  # move the window forward with overlap

    return chunks

# Example usage
if __name__ == "__main__":
    sample_text = (
        "This is a sample text to demonstrate chunking. "
        "It will be split into smaller parts for embedding and retrieval purposes. "
        "Each chunk contains metadata about the source, page, and title."
    )

    chunks = chunk_text(sample_text, page_no=1, title="Sample Document", max_tokens=10, overlap=3)
    for idx, chunk in enumerate(chunks):
        print(f"Chunk {idx+1}:")
        print("ID:", chunk['id'])
        print("Text:", chunk['text'])
        print("Meta:", chunk['meta'])
        print("="*50)
