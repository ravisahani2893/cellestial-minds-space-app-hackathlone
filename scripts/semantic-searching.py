
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from tqdm import tqdm

PAPERS_FILE = "data/papers.json"
FAISS_INDEX_FILE = "data/papers_index.faiss"
META_FILE = "data/papers_meta.json"
EMBED_MODEL = "all-MiniLM-L6-v2"
def make_corpus_item(p):
    # Compose a single text block to encode
    parts = []
    if p.get("title"): parts.append(p["title"])
    if p.get("abstract"): parts.append(p["abstract"])
    if p.get("results"): parts.append(p["results"])
    if p.get("conclusion"): parts.append(p["conclusion"])
    # fallback use full_text
    if not parts and p.get("full_text"):
        parts.append(p["full_text"][:2000])
    return "\n\n".join(parts)

def main():
    with open(PAPERS_FILE, "r", encoding="utf-8") as f:
        papers = json.load(f)

    if not papers:
        print("No papers found in", PAPERS_FILE)
        return

    print(f"Loaded {len(papers)} papers.")

    corpus = [make_corpus_item(p) for p in papers]

    print("Loading embedding model:", EMBED_MODEL)
    model = SentenceTransformer(EMBED_MODEL)

    print("Computing embeddings...")
    embeddings = model.encode(corpus, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)

    d = embeddings.shape[1]
    print("Embedding dim:", d)

    # Build FAISS index
    index = faiss.IndexFlatIP(d)  # cosine via normalized vectors => inner product
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_FILE)
    print("Saved FAISS index to", FAISS_INDEX_FILE)

    # Save meta (we will keep the original paper dict and the corpus text)
    meta = [{"pmcid": p.get("pmcid"), "title": p.get("title"), "meta_title": p.get("meta_title"),
             "source_link": p.get("source_link"), "abstract": p.get("abstract"),
             "results": p.get("results"), "conclusion": p.get("conclusion"),
             "full_text_preview": (p.get("full_text") or "")[:2000]} for p in papers]

    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("Saved metadata to", META_FILE)
    print("Index build done.")

if __name__ == "__main__":
    main()
