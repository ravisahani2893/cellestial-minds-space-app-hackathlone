import streamlit as st
import json
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, util

# -----------------------------
# Load Model and Tokenizer
# -----------------------------
@st.cache_resource
def load_summarizer():
    model_name = "allenai/led-large-16384-arxiv"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return tokenizer, model, device

# -----------------------------
# Load Embedding Model
# -----------------------------
@st.cache_resource
def load_embedder():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# -----------------------------
# Load Paper Data
# -----------------------------
@st.cache_data
def load_papers():
    with open("data/papers.json", "r", encoding="utf-8") as f:
        papers = json.load(f)
    return papers

# -----------------------------
# Summarization Function
# -----------------------------
def generate_summary(text, tokenizer, model, device):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=16000,
        truncation=True
    ).to(device)

    summary_ids = model.generate(
        **inputs,
        max_length=512,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True
    )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# -----------------------------
# Search Function
# -----------------------------
def search_papers(query, papers, embedder, top_k=3):
    corpus = [p["title"] + " " + p.get("abstract", "") for p in papers]
    corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)[0]
    return [papers[hit["corpus_id"]] for hit in hits]

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Research Paper Summarizer", layout="wide")
st.title("🧠 Research Paper Summarizer")
st.markdown("Enter your research query to get summarized insights from papers.")

# Load models and data
tokenizer, model, device = load_summarizer()
embedder = load_embedder()
papers = load_papers()

query = st.text_input("🔍 Enter your query (e.g., 'Effects of microgravity on immune system'):")

if st.button("Generate Summary"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Searching and summarizing papers..."):
            relevant_papers = search_papers(query, papers, embedder)
            st.success(f"Found {len(relevant_papers)} relevant papers.")

            for paper in relevant_papers:
                title = paper.get("title", "")
                abstract = paper.get("abstract", "")
                results = paper.get("results", "")

                input_text = f"Title: {title}\n\nAbstract: {abstract}\n\nResults: {results}"
                summary = generate_summary(input_text, tokenizer, model, device)

                with st.expander(f"📄 {title}"):
                    st.markdown(f"**Summary:** {summary}")
                    st.markdown("---")
                    st.markdown(f"**Original Abstract:** {abstract}")

