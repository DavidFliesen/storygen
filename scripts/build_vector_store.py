import argparse
import json
from pathlib import Path
import numpy as np
import faiss
from openai import OpenAI

from common import read_json, write_json, caption_to_text, story_to_text, VECTOR_DIR

EMBED_MODEL = "text-embedding-3-small"

def embed_texts(client, texts, batch_size=100):
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        response = client.embeddings.create(model=EMBED_MODEL, input=batch)
        vectors.extend([item.embedding for item in response.data])
    return np.array(vectors, dtype="float32")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-unused", action="store_true", help="Also include unused ideas from stories.json in memory.")
    args = parser.parse_args()

    client = OpenAI()

    docs = []

    captions = read_json("captions.json", [])
    for i, item in enumerate(captions):
        text = caption_to_text(item)
        if text:
            docs.append({
                "id": f"caption-{i+1}",
                "source": "captions.json",
                "status": "used",
                "text": text
            })

    stories = read_json("stories.json", [])
    for story in stories:
        status = story.get("status", "unused")
        if status == "used" or args.include_unused:
            text = story_to_text(story)
            if text:
                docs.append({
                    "id": story.get("id", f"story-{len(docs)+1}"),
                    "source": "stories.json",
                    "status": status,
                    "title": story.get("title", ""),
                    "text": text
                })

    if not docs:
        raise SystemExit("No captions or stories found to vectorize.")

    texts = [d["text"] for d in docs]
    vectors = embed_texts(client, texts)
    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(VECTOR_DIR / "stories.faiss"))
    write_json(VECTOR_DIR / "metadata.json", docs)

    print(f"Built FAISS memory with {len(docs)} documents.")

if __name__ == "__main__":
    main()
