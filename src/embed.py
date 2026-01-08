from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from ingest import load_pdfs, chunk_documents

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_PATH = "../data/faiss.index"
META_PATH = "../data/chunks.pkl"


def create_embeddings(chunks):
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings


def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


if __name__ == "__main__":
    print("Loading documents...")
    documents = load_pdfs()
    chunks = chunk_documents(documents)

    print("Creating embeddings...")
    embeddings = create_embeddings(chunks)

    print("Building FAISS index...")
    index = build_faiss_index(np.array(embeddings))

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print("✅ FAISS index created successfully")
    print(f"Total chunks indexed: {len(chunks)}")
