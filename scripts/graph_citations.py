import json
import networkx as nx
import matplotlib.pyplot as plt
import community as community_louvain
from pathlib import Path
# Fichier des articles neuroscientifiques uniquement
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data_graph"
output_dir = base_dir / "outputs"
neuro_file = data_dir / "dblp_filtered_light.jsonl"
image_output = output_dir/"neuro_citation_graph_internal.png"

# 1. Charger les articles neuroscientifiques
neuro_articles = {}
with open(neuro_file, "r", encoding="utf-8") as f:
    for line in f:
        article = json.loads(line)
        neuro_articles[article["id"]] = article

neuro_ids = set(neuro_articles.keys())

# 2. Construire le graphe de citations internes (orienté)
G = nx.DiGraph()

for source_id, article in neuro_articles.items():
    G.add_node(source_id, label=article.get("title", ""), year=article.get("year", 0))

    references = article.get("references", [])
    if isinstance(references, list):
        for cited_id in references:
            if cited_id in neuro_ids:
                G.add_edge(source_id, cited_id)

gexf_output = output_dir / "neuro_citation_graph_light.gexf"
nx.write_gexf(G, gexf_output)
print(f"💾 Graphe orienté sauvegardé : {gexf_output}")
print(f"✅ Graphe interne : {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes (citations internes)")

# 3. Clustering (communautés Louvain sur graphe non orienté)
undirected = G.to_undirected()
partition = community_louvain.best_partition(undirected)
nx.set_node_attributes(G, partition, "community")

# 4. Affichage et sauvegarde de l’image
plt.figure(figsize=(15, 15))
pos = nx.spring_layout(G, k=0.1, seed=42)

# Couleurs selon les communautés
communities = [partition.get(node, 0) for node in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_size=30, node_color=communities, cmap=plt.cm.viridis)
nx.draw_networkx_edges(G, pos, alpha=0.3, arrows=True)

plt.axis("off")
plt.title("Graphe orienté des citations neuroscientifiques", fontsize=16)
plt.tight_layout()
plt.savefig(image_output, format="PNG", dpi=300)
plt.show()

print(f"🖼️ Image du graphe enregistrée : {image_output}")
