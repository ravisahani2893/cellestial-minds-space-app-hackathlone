

from pyvis.network import Network
import networkx as nx
from pathlib import Path
import json

def visualize_triplets(triplets, output_file):
    G = nx.DiGraph()

    for subj, pred, obj in triplets:
        G.add_node(subj, title=subj)
        G.add_node(obj, title=obj)
        G.add_edge(subj, obj, label=pred)

    net = Network(notebook=False, directed=True, height="750px", width="100%")
    net.from_nx(G)
    net.write_html(output_file)
    print(f" Knowledge graph saved to {output_file}")

def load_triplets_from_json(json_path):
    """
    Load triplets from a JSON file (list of dicts with subject, predicate, object).
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {json_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    triplets = [(d["subject"], d["relation"], d["object"]) for d in data]
    return triplets



if __name__ == "__main__":
    json_path = "outputs/striplets-new.json"
    output_file = "outputs/knowledge_graph.html"

    triplets = load_triplets_from_json(json_path)

    visualize_triplets(triplets,output_file)
