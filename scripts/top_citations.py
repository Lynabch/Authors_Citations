import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data_graph"
output_dir = base_dir / "outputs"

gexf_file = data_dir / "neuro_citation_graph_light.gexf"
G = nx.read_gexf(gexf_file)
# 🔢 Extraire les 30 articles les plus cités
top_nodes = sorted(G.in_degree(), key=lambda x: x[1], reverse=True)[:20]
top_node_ids = [node for node, _ in top_nodes]

# 🕸️ Construire un sous-graphe
H = G.subgraph(top_node_ids).copy()

# 🧭 Positionnement
pos = nx.spring_layout(H, k=0.4, seed=42)

# 🎨 Affichage avec titres
plt.figure(figsize=(15, 10))
nx.draw_networkx_nodes(H, pos, node_size=600, node_color="lightblue")
nx.draw_networkx_edges(H, pos, arrows=True, arrowstyle="->", alpha=0.4)
nx.draw_networkx_labels(H, pos, labels=nx.get_node_attributes(H, "label"), font_size=8)

plt.title("Zoom : Top 20 articles les plus cités (avec titres)", fontsize=14)
plt.axis("off")
plt.tight_layout()
plt.show()
