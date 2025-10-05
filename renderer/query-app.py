import streamlit as st
import json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

FAISS_INDEX_FILE = "data/papers_index.faiss"
META_FILE = "data/papers_meta.json"
EMBED_MODEL = "all-minilm-l6-v2"

st.set_page_config(page_title="NASA Space Biology Knowledge Engine", layout="wide")
st.title(" NASA Space Biology Knowledge Engine (Prototype)")
st.write("Search and summarize findings from NASA space biology publications.")

# Load meta & index (single-time)
@st.cache_data(show_spinner=True)
def load_index_and_meta():
    # Load FAISS index
    index = faiss.read_index(FAISS_INDEX_FILE)

    # Load meta
    with open(META_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Load model
    model = SentenceTransformer(EMBED_MODEL)
    return index, meta, model

index, meta, model = load_index_and_meta()

# Query input
query = st.text_input("Ask a question or enter a search query:", value="", max_chars=200)

col1, col2 = st.columns([3, 1])

with col2:
    top_k = st.number_input("Top K", value=5, min_value=1, max_value=20, step=1)

if st.button("Search") and query.strip():
    with st.spinner("Searching..."):
        qvec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = index.search(qvec, top_k)
        scores = D[0]
        ids = I[0]

    st.success(f"Found {len(ids)} results.")
    for rank, (idx, score) in enumerate(zip(ids, scores), start=1):
        if idx < 0 or idx >= len(meta):
            continue
        item = meta[idx]
        st.markdown(f"#### {rank}. {item.get('title') or item.get('meta_title')}")
        st.write(f"**PMCID:** {item.get('pmcid')}   •   **Score:** {score:.4f}")
        if item.get("abstract"):
            st.write("**Abstract:**")
            st.write(item["abstract"][:1000] + ("..." if len(item["abstract"]) > 1000 else ""))
        elif item.get("full_text_preview"):
            st.write(item["full_text_preview"][:1000] + ("..." if len(item["full_text_preview"]) > 1000 else ""))
        # show results/conclusion if present
        if item.get("results"):
            st.write("**Results excerpt:**")
            st.write(item["results"][:800] + ("..." if len(item["results"]) > 800 else ""))
        if item.get("conclusion"):
            st.write("**Conclusion excerpt:**")
            st.write(item["conclusion"][:800] + ("..." if len(item["conclusion"]) > 800 else ""))
        st.markdown(f"[Open source]({item.get('source_link')})")
        st.markdown("---")
else:
    st.info("Enter a query and click Search to begin. Example queries: 'plant growth microgravity', 'radiation DNA damage', 'bone loss astronaut'.")
