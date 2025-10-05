import pandas as pd
import re
import requests
import time
import json
from tqdm import tqdm

CSV_URL = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
OUT_FILE = "papers.json"
MAX_PAPERS = 608


def cleanup_data(text: str):
 
    
    # Normalize minus signs (U+2212 → hyphen)
    text = text.replace("−", "-")

    # Step 1: Decode Unicode escapes
    text = text.encode('utf-8').decode('unicode_escape')

    # Step 2: Optional: Remove extra backslashes (if any)
    text = text.replace('\\', '')
    
    # Normalize multiple spaces / weird unicode spaces
    text = re.sub(r"\s+", " ", text).strip()

    text = re.sub(r'^\s*\d+(\.\d+)*\s*\.?\s*', '', text, flags=re.MULTILINE)

    # Optional: Remove extra empty lines
    text = re.sub(r'\n\s*\n', '\n', text).strip()

    # 1. Remove figure references like (Fig. 1A), (Fig. 1B–D)
    text = re.sub(r"\(Fig\.[^)]*\)", "", text)

    # 2. Remove table references like (Table 1), (Table 2)
    text = re.sub(r"\(Table[^)]*\)", "", text)

    # Remove "Refer to Fig. X" (X can be 1, 2A, 3B–D etc.)
    text = re.sub(r"Refer to Fig\.[^\s.]*\.?", "", text)

    # 3. Remove "for full review see ..." notes
    text = re.sub(r"\(for full review see[^)]*\)", "", text, flags=re.IGNORECASE)

    return text

def fetch_space_biology_data_bioc(pmcid: str):

    
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmcid}/unicode"
    # print(pmcid)
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching {pmcid}: {response.status_code}")
        return None

    try:
        paper_json = response.json()
        # print(paper_json)
    except Exception as e:
        print(f"Failed to parse JSON for {pmcid}: {e}")
        return None
    
    time.sleep(1)

    return paper_json



url = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
df = pd.read_csv(url)


def get_all_paper_data(df):

    paper_metadata = list()
    for index, row in df.iterrows():
        match = re.search(r'(PMC\d+)', row['Link'])
        if match:
         pmc_id = match.group(1)
         paper_metadata.append(pmc_id)

    return paper_metadata     


table_metadata_ids = get_all_paper_data(df)

def process_space_biology_data(metada_json_data):
    paragraph_data = metada_json_data[0]["documents"][0]
    passsages =paragraph_data['passages']


    rows = []
    current_l1 = None
    current_l2 = None

    for item in passsages:
        passagge_data = item["text"]
        t = item['infons']['type']
        text = cleanup_data(passagge_data)

        if t == "title_1":
            current_l1 = text
            current_l2 = None
        elif t == "title_2":
            current_l2 = text
        elif t == "paragraph":
            rows.append({
            "level_1": current_l1,
            "level_2": current_l2,
            "text": text
            })


    return rows

def fetch_all_nasa_metadata_info(metadata_list):

    metadata_raw_json_response_list=list()

    raw_json_data=fetch_space_biology_data_bioc(metadata_list[1])
    space_engine_processed_data = process_space_biology_data(raw_json_data)
    row_json = json.dumps(space_engine_processed_data)


    print(row_json)

    # for metadata_id in metadata_list:
    #     raw_json_data=fetch_space_biology_data_bioc(metadata_id)
        
    #     space_engine_processed_data = process_space_biology_data(raw_json_data)

    #     try:
    #         raw_json_data = json.loads(space_engine_processed_data)
    #         print("Valid JSON")
    #     except json.JSONDecodeError:
    #         print("Invalid JSON")

    #     metadata_raw_json_response_list.append(raw_json_data)


    # return metadata_raw_json_response_list  


metadata_raw_json_response_list=fetch_all_nasa_metadata_info(table_metadata_ids)


# print(metadata_raw_json_response_list[0])




    

# paper3_response = fetch_space_biology_data_bioc("PMC11988870")



# structured = {}
# stack = []  # keep track of nested titles
# paragraph_data = paper3_response[0]["documents"][0]
# passsages =paragraph_data['passages']


# rows = []
# current_l1 = None
# current_l2 = None

# for item in passsages:
#     passagge_data = item["text"]
#     t = item['infons']['type']
#     text = cleanup_data(passagge_data)

#     if t == "title_1":
#         current_l1 = text
#         current_l2 = None
#     elif t == "title_2":
#             current_l2 = text
#     elif t == "paragraph":
#         rows.append({
#             "level_1": current_l1,
#             "level_2": current_l2,
#             "text": text
#         })


# row_json = json.dumps(rows)        

# print(row_json)

def extract_pmcid(link):
    """Extract numeric PMCID (without 'PMC' prefix) from a link if present."""
    if not isinstance(link, str):
        return None
    m = re.search(r'PMC(\d+)', link)
    return m.group(1) if m else None

def fetch_bioc_sections(pmcid):
    """
    Fetch BioC JSON for PMCID and extract sections.
    Return dict: {title, abstract, results, conclusion, raw_passages_text}
    """
    # Use PMC prefix in URL (BioC expects 'PMC{num}')
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC{pmcid}/unicode"
    try:
        r = requests.get(url, timeout=15)
    except Exception as e:
        print(f"Error requesting {pmcid}: {e}")
        return None

    if r.status_code != 200:
        # Not found or blocked
        # print(f"Status {r.status_code} for PMC{pmcid}")
        return None

    try:
        bio = r.json()
    except Exception as e:
        # Could be non-json or parse error
        # print(f"JSON parse error for PMC{pmcid}: {e}")
        return None

    # Navigate expected BioC structure: [0]["documents"][0]["passages"]
    try:
        docs = bio[0].get("documents", [])
        if not docs:
            return None
        passages = docs[0].get("passages", [])
    except Exception:
        return None

    out = {"pmcid": pmcid, "title": "", "abstract": "", "results": "", "conclusion": "", "full_text": ""}

    for p in passages:
        infons = p.get("infons", {}) or {}
        section_type = (infons.get("section_type") or "").lower()
        text = p.get("text", "") or ""
        out["full_text"] += text + "\n"

        # heuristics to populate fields (robust to various tags)
        if ("title" in section_type or "heading" in section_type) and not out["title"]:
            out["title"] = text.strip()
        elif "abstract" in section_type:
            out["abstract"] += text.strip() + " "
        elif any(k in section_type for k in ["results", "finding", "findings", "result"]):
            out["results"] += text.strip() + " "
        elif any(k in section_type for k in ["conclusion", "concluding", "discussion", "summary"]):
            out["conclusion"] += text.strip() + " "

    # Fallbacks: if title empty, try first passage text
    if not out["title"] and passages:
        out["title"] = passages[0].get("text", "").strip()[:200]

    # Trim whitespace
    for k in ["title", "abstract", "results", "conclusion", "full_text"]:
        out[k] = (out[k] or "").strip()

    return out

def main():
    print("Loading CSV...")
    df = pd.read_csv(CSV_URL)
    # CSV in your case has Title and Link
    if "Link" not in df.columns:
        raise SystemExit("CSV does not contain 'Link' column. Check CSV URL.")

    df["PMCID"] = df["Link"].apply(extract_pmcid)
    df = df[df["PMCID"].notna()].reset_index(drop=True)
    print(f"Found {len(df)} rows with PMCID links.")

    to_fetch = df if MAX_PAPERS is None else df.head(MAX_PAPERS)

    papers = []
    for _, row in tqdm(to_fetch.iterrows(), total=len(to_fetch), desc="Fetching PMC"):
        pmcid = str(row["PMCID"])
        title_meta = row.get("Title", "") or ""
        fetched = fetch_bioc_sections(pmcid)
        if fetched:
            # Keep metadata from CSV and fetched content
            fetched["meta_title"] = title_meta
            fetched["source_link"] = row["Link"]
            papers.append(fetched)
        time.sleep(0.35)  

    print(f"Fetched {len(papers)} papers. Saving to {OUT_FILE} ...")
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)

    print("Over.")

if __name__ == "__main__":
    main()
