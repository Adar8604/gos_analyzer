import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load your JSON list

with open("guidelines_2.json", "r", encoding="utf-8") as f:
    guidelines = json.load(f)

# -----------------------------
# Embedding model
# Recommended:
#   BAAI/bge-large-en-v1.5 (best)
#   BAAI/bge-base-en-v1.5 (faster)
# -----------------------------
model = SentenceTransformer("BAAI/bge-base-en-v1.5")

# Create text for embedding
texts = []

for item in guidelines:
    text = f"""
{item['guideline']}\n
{item['embedding_text']}
"""
    texts.append(text.strip())

# Generate embeddings
embeddings = model.encode(
    texts,
    normalize_embeddings=True,
    convert_to_numpy=True,
    show_progress_bar=True
)

# Create FAISS Index
dimension = embeddings.shape[1]

# cosine similarity
index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

print(f"Indexed {index.ntotal} guidelines.")

# Save Index
faiss.write_index(index, "lea_guidelines_2.faiss")

# Save metadata separately
with open("lea_metadata_2.json", "w", encoding="utf-8") as f:
    json.dump(guidelines, f, indent=2)

print("Saved FAISS index and metadata.")