import pandas as pd
import networkx as nx
from itertools import combinations
from collections import Counter
import community as community_louvain
import matplotlib.pyplot as plt
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data_graph"
output_dir = base_dir / "outputs"
# 📥 Charger les données neurosciences filtrées
input_file = data_dir / "dblp_filtered_light.jsonl"
df = pd.read_json(input_file, lines=True)

# 📊 Construction du graphe de co-auteurs
G = nx.Graph()
edge_counter = Counter()

for _, row in df.iterrows():
    authors = [a["name"] for a in row["authors"] if "name" in a]
    for a1, a2 in combinations(authors, 2):
        edge = tuple(sorted((a1, a2)))
        edge_counter[edge] += 1

for (a1, a2), weight in edge_counter.items():
    G.add_edge(a1, a2, weight=weight)

print(f"✅ Graphe construit avec {G.number_of_nodes()} nœuds et {G.number_of_edges()} arêtes.")

# Clustering Louvain
partition = community_louvain.best_partition(G)
nx.set_node_attributes(G, partition, "community")

# Centralité degré 
degree_centrality = nx.degree_centrality(G)
nx.set_node_attributes(G, degree_centrality, "degree")

# Sous-graphe des 200 nœuds les plus connectés
top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:200]
subgraph = G.subgraph([n for n, _ in top_nodes])

#  Visualisation
plt.figure(figsize=(14, 10))
pos = nx.kamada_kawai_layout(subgraph)

node_color = [partition.get(n, 0) for n in subgraph.nodes()]
node_size = [degree_centrality.get(n, 0) * 3000 for n in subgraph.nodes()]

nx.draw(subgraph, pos,
        node_color=node_color,
        node_size=node_size,
        edge_color="#cccccc",
        with_labels=False)

# Labels pour les nœuds très connectés
important_labels = {n: n for n in subgraph.nodes() if degree_centrality.get(n, 0) > 0.05}
nx.draw_networkx_labels(subgraph, pos, labels=important_labels, font_size=8)

plt.title("🧠 Graphe de co-auteurs – Neurosciences (Top 200, clusters Louvain)")
plt.axis("off")
plt.tight_layout()

# Sauvegarde en image
image_file = output_dir / "graph_neuro_no_pagerank.png"
plt.savefig(image_file, dpi=300)
print(f"🖼️ Graphique sauvegardé dans : {image_file}")
# Export Gephi
gexf_file = data_dir / "graph_neuro_no_pagerank.gexf"
nx.write_gexf(G, gexf_file)
print(f"📦 Fichier GEXF exporté pour Gephi : {gexf_file}")
#  Extraire les infos pour tous les auteurs
data = []

for node in G.nodes():
    data.append({
        "Auteur": node,
        "Degré": G.degree(node),
        "Communauté": partition.get(node)
    })

# Convertir en DataFrame
df_stats = pd.DataFrame(data)

# Trier par degré décroissant (optionnel)
df_stats = df_stats.sort_values("Degré", ascending=False)

# Exporter en CSV
excel_file = output_dir / "stats_auteurs_neuro.xlsx"
df_stats.to_csv(excel_file, index=False)
print(f"📦 Stats exportées dans : {excel_file}")
