from pathlib import Path
import numpy as np
import faiss
from openai import OpenAI
from common import read_json, story_to_text, VECTOR_DIR

EMBED_MODEL = "text-embedding-3-small"

def load_memory():
    index_path = VECTOR_DIR / "stories.faiss"
    metadata_path = VECTOR_DIR / "metadata.json"
    if not index_path.exists() or not metadata_path.exists():
        return None, []
    index = faiss.read_index(str(index_path))
    metadata = read_json(metadata_path, [])
    return index, metadata

def find_similar_story(story, threshold=0.80, top_k=5):
    index, metadata = load_memory()
    if index is None:
        return {
            "is_duplicate": False,
            "score": 0.0,
            "matches": [],
            "reason": "No FAISS vector store found."
        }

    client = OpenAI()
    text = story_to_text(story)
    response = client.embeddings.create(model=EMBED_MODEL, input=[text])
    vector = np.array([response.data[0].embedding], dtype="float32")
    faiss.normalize_L2(vector)

    scores, indices = index.search(vector, min(top_k, len(metadata)))
    matches = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        doc = metadata[idx]
        matches.append({
            "score": float(score),
            "id": doc.get("id", ""),
            "title": doc.get("title", ""),
            "source": doc.get("source", ""),
            "text_preview": doc.get("text", "")[:240]
        })

    best_score = matches[0]["score"] if matches else 0.0

    return {
        "is_duplicate": best_score >= threshold,
        "score": best_score,
        "matches": matches,
        "reason": "Similarity check complete."
    }
