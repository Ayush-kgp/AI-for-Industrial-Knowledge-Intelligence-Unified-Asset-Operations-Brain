from sentence_transformers import SentenceTransformer

# Load BGE-M3 model globally so it's only loaded once per worker
try:
    # Use device='cpu' explicitly to avoid warnings if no GPU is available, 
    # or let it auto-detect. BGE-M3 is heavy but runs on CPU for small batches.
    embedder_model = SentenceTransformer("BAAI/bge-m3")
except Exception as e:
    print(f"Warning: Failed to load embedder model. Is torch installed? {e}")
    embedder_model = None

def generate_embedding(text: str) -> list[float]:
    """
    Generates a dense vector embedding for the given text using BGE-M3.
    """
    if not embedder_model:
        raise RuntimeError("Embedder model not loaded.")
        
    # BGE-M3 outputs vectors of dimension 1024
    embedding = embedder_model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
