# NASA Space Apps Challenge 2025 — Cellestial Minds

Enable a new era of human space exploration! This project gathers, indexes and analyzes space-biology literature and publications to help teams prepare for human missions to the Moon and Mars.

---

## Features

- Extract Nasa space biology publication papers from metadata and converted into Clean Structured Data
- Trained all-MiniLM-L6-v2 sentence transformer model for semantic search of textual data.
- Trained allenai/led-large-16384-arxiv model for summarization of the Topic. 
- Provide search / retrieval utilities and simple Streamlit UI for exploration.
- Scripts included to create triplets for Knowledge graph exploration.


---

## Repo structure (high level)

- `space-enginer.py` & `fetch.py` — core data-processing / ingestion scripts.
- `semantic-searching.py` & `summarizer.py` — builds embeddings and a FAISS index from `papers.json` / other JSON files.
- `data/papers.json`, `data/structured_data.json`, `data/summaries.json`, `data/paper_index.faiss`,
`data/grouped_papers.json`, `data/paper_meta.json` — Structured JSON data fetched after data processing from Unstructured data.
- `scripts/build_kg.py`,`scripts/ontology.py` - Uses Gemni to extract Ontology and create Triplets from data for knowldge graph creation and uses pyvis to create an inbterative html of the knowledge graphs

---

## Key libraries used

The code in this repository uses (but may not be limited to) the following Python libraries:

- `sentence-transformers` (for embedding models)
- `faiss` (indexing / nearest neighbor search)
- `numpy`
- `tqdm`
- `pandas`
- `streamlit` (UI)
- `transformers` (training allenai/led-large, tokenizers)
- `datasets` (Hugging Face datasets utilities)
- `torch` (PyTorch)
- `scikit-learn` (`sklearn`, for train/test splits etc.)
- `evaluate` (Hugging Face evaluation tools)

> Note: exact imports can be found in each script. If you add or remove libraries while developing, update `requirements.txt` accordingly.

---

## Install / setup

Below are two recommended ways to install dependencies: using Conda (recommended for `faiss` + PyTorch compatibility) or using `pip` inside a virtualenv.

### Conda (recommended)

```bash
# create environment
conda create -n nasa-hackathon python=3.10 -y
conda activate nasa-hackathon

# install PyTorch (choose appropriate CUDA / CPU build from https://pytorch.org)
conda install pytorch torchvision torchaudio cpuonly -c pytorch -y

# install faiss (CPU)
conda install -c pytorch faiss-cpu -y

# common python packages
pip install -r requirements.txt
```

### Pip (virtualenv)

```bash
python -m venv .venv
source .venv/bin/activate

# faiss pip wheels are less consistent across platforms — prefer conda. If you must use pip:
# CPU-only wheel (if available for your Python version):
pip install faiss-cpu || pip install faiss

pip install -r requirements.txt
```

### Example `requirements.txt`

```
sentence-transformers
faiss-cpu
numpy
pandas
tqdm
streamlit
transformers
datasets
torch
scikit-learn
evaluate
flask
```

---

## How to use

### 1) Run semantic-searching.py file to build metadata and index files for Semantic searching of data 


```bash
python scripts/semantic-searching.py 
```

### 2) Run Semantic search app by running query-app.py script

```bash
python renderer/query-app.py 
```

### 3) Run summarizer.py file to build metadata files for Summarising topic data


```bash
python scripts/summarizer.py 
```

### 4) Run Semantic search app by running query-app.py script

```bash
python renderer/summary-app.py 
```

The script in this repo uses `sentence-transformers` to compute embeddings and `faiss` to build an index. After running it you should have:

- `papers_index.faiss` — FAISS binary index file
- `papers_meta.json` — metadata for the vectors (Title, Abstract, Methods, Conclusions, Discussions, Results, References , etc.)

