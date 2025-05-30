#pas encore executé executer ça en priorité la semaine prochaine
import pandas as pd
import networkx as nx
from itertools import combinations
from collections import Counter
import community as community_louvain
import matplotlib.pyplot as plt

# 📥 Charger les données neurosciences filtrées
input_file = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_filtered_light.jsonl"
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

# 🧠 Clustering Louvain
partition = community_louvain.best_partition(G)
nx.set_node_attributes(G, partition, "community")

# 📈 Centralité PageRank
pagerank = nx.pagerank(G)
nx.set_node_attributes(G, pagerank, "pagerank")

# 🎯 Sous-graphe des 200 auteurs les plus centraux
top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:200]
subgraph = G.subgraph([n for n, _ in top_nodes])

# 🎨 Visualisation
plt.figure(figsize=(14, 10))
pos = nx.kamada_kawai_layout(subgraph)

node_color = [partition.get(n, 0) for n in subgraph.nodes()]
node_size = [pagerank.get(n, 0) * 4000 for n in subgraph.nodes()]

nx.draw(subgraph, pos,
        node_color=node_color,
        node_size=node_size,
        edge_color="#cccccc",
        with_labels=False)

# Labels pour les nœuds très centraux
important_labels = {n: n for n in subgraph.nodes() if pagerank.get(n, 0) > 0.01}
nx.draw_networkx_labels(subgraph, pos, labels=important_labels, font_size=8)

plt.title("🧠 Graphe de co-auteurs – Neurosciences (Top 200, clusters Louvain)")
plt.axis("off")
plt.tight_layout()

# 💾 Sauvegarde en image
plt.savefig("C:/Users/baouc/Documents/GRAPH_DATA/data_graph/graph_neuroscience_top200.png", dpi=300)
print("🖼️ Graphique sauvegardé dans : graph_neuroscience_top200.png")

# 💾 Export Gephi
nx.write_gexf(G, "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/graph_neuroscience.gexf")
print("📦 Fichier GEXF exporté pour Gephi : graph_neuroscience.gexf")