import re
import numpy as np
from sentence_transformers import SentenceTransformer

# Load once
model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

def split_sentences(text):
    """
    Split STR into sentences while keeping decimal numbers intact.
    """

    text = text.replace("\n", " ")

    pattern = r'(?<=[.!?])\s+(?=[A-Z])'

    sentences = re.split(pattern, text)

    return [s.strip() for s in sentences if s.strip()]


def cosine(a, b):
    return np.dot(a, b)


def semantic_segment(text, threshold=0.70):

    sentences = split_sentences(text)

    if len(sentences) <= 1:
        return [text]

    embeddings = model.encode(
        sentences,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    segments = []

    current = [sentences[0]]

    for i in range(1, len(sentences)):

        similarity = cosine(
            embeddings[i - 1],
            embeddings[i],
        )


        if similarity < threshold:

            segments.append(" ".join(current))
            current = [sentences[i]]

        else:

            current.append(sentences[i])

    if current:
        segments.append(" ".join(current))

    return segments