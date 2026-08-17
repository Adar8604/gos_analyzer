from pathlib import Path
import json

import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent

# Files
INDEX_PATH = BASE_DIR / "lea_guidelines_2.faiss"
METADATA_PATH = BASE_DIR / "lea_metadata_2.json"

# Load FAISS index
index = faiss.read_index(str(INDEX_PATH))

# Load embedding model
model = SentenceTransformer("BAAI/bge-base-en-v1.5")

# Load metadata
with METADATA_PATH.open("r", encoding="utf-8") as f:
    metadata = json.load(f)


def search(query_text, k=5, threshold=0.50):
    query = model.encode(
        query_text,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).reshape(1, -1)

    scores, ids = index.search(query, k)

    results = []

    for score, idx in zip(scores[0], ids[0]):
        if idx == -1 or score < threshold:
            continue

        item = metadata[idx]

        results.append({
            "score": float(score),
            "guideline": item["guideline"],
            "category": item["category"],
            "target_leas": item["target_leas"],
            "conditions": item["conditions"],
        })

    return results