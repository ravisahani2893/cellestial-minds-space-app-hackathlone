import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm
import torch

# Load model and tokenizer
model_name = "allenai/led-large-16384-arxiv"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Load your data (example: papers.json)
with open("data/papers.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

papers = papers[:10]
summaries = []

for paper in tqdm(papers, desc="Summarizing papers"):
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    results = paper.get("results", "")

    input_text = f"Title: {title}\n\nAbstract: {abstract}\n\nResults: {results}"
    
    # Tokenize input
    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        max_length=16000,
        truncation=True
    ).to(device)
    
    # Generate summary
    summary_ids = model.generate(
        **inputs,
        max_length=512,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True
    )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    summaries.append({
        "pmcid": paper["pmcid"],
        "title": title,
        "summary": summary
    })

# Save summaries
with open("data/summaries.json", "w", encoding="utf-8") as f:
    json.dump(summaries, f, indent=2)