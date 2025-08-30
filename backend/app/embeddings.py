import chromadb
from sentence_transformers import SentenceTransformer

# --- GLOBAL VARIABLES ---
# We initialize the model and collection to None. They will be loaded
# on-demand the first time they are needed.
model = None
collection = None

# --- LAZY LOADING FUNCTIONS ---

def get_model():
    """
    Loads the Sentence Transformer model only once.
    This prevents the slow model download from blocking server startup.
    """
    global model
    if model is None:
        print("Model not loaded. Initializing and downloading now...")
        # This is the line that can be slow on the first run
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Model loaded successfully.")
    return model

def get_collection():
    """
    Initializes the ChromaDB collection only once.
    """
    global collection
    if collection is None:
        print("Database collection not initialized. Connecting...")
        client = chromadb.PersistentClient(path="./chroma_db")
        try:
            collection = client.get_collection(name="ncert_chunks")
        except Exception:
            # If the collection doesn't exist, create it.
            collection = client.create_collection(name="ncert_chunks")
        print("Database collection is ready.")
    return collection

# --- CORE LOGIC ---

def embed_texts(texts: list[str]):
    """Convert a list of texts into embeddings using the loaded model."""
    # Ensure the model is loaded before trying to use it.
    current_model = get_model()
    return current_model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

def retrieve_answer(query: str, top_k: int = 4):
    """Retrieve top-k most relevant chunks from ChromaDB for a given query."""
    col = get_collection()
    q_emb = embed_texts([query])[0]

    results = col.query(
        query_embeddings=[q_emb.tolist()],
        n_results=top_k,
        include=["metadatas", "documents", "distances"]
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    evidence = []
    for d, m, dist in zip(docs, metas, distances):
        evidence.append({
            "text": d,
            "source": m,
            "score": float(dist)
        })

    return {
        "query": query,
        "evidence": evidence,
        "note": "This is a retrieval-based answer. For a natural language response, this evidence would be passed to an LLM."
    }

def upsert_chunks(chunks: list[dict]):
    """Insert or update chunks into the ChromaDB collection."""
    col = get_collection()
    ids = [c["id"] for c in chunks]
    docs = [c["text"] for c in chunks]
    metas = [c["meta"] for c in chunks]
    embs = embed_texts(docs)

    col.add(
        ids=ids,
        documents=docs,
        metadatas=metas,
        embeddings=embs.tolist()
    )

