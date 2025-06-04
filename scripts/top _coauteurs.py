import networkx as nx
import matplotlib.pyplot as plt
import community as community_louvain
from pathlib import Path

# Fichier du graphe de co-auteurs
base_dir = Path(__file__).resolve().parent.parent
data_path = base_dir / "data_graph" / "graph_neuro_no_pagerank.gexf"
G = nx.read_gexf(data_path)

# Top 30 auteurs par degré
top_authors = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:50]
top_author_ids = [node for node, _ in top_authors]

# Sous-graphe
H = G.subgraph(top_author_ids).copy()

# Appliquer Louvain (nécessite un graphe non orienté)
partition = community_louvain.best_partition(H.to_undirected())

#  Ajouter l’attribut 'community' dans les nœuds
nx.set_node_attributes(H, partition, "community")

# Couleurs des communautés
communities = [partition[node] for node in H.nodes()]
labels = {node: H.nodes[node].get("label", node) for node in H.nodes()}

# Positionnement
pos = nx.spring_layout(H, k=0.5, seed=42)

# Affichage
plt.figure(figsize=(15, 10))
nx.draw_networkx_nodes(H, pos, node_size=600, node_color=communities, cmap=plt.cm.Set2)
nx.draw_networkx_edges(H, pos, alpha=0.3)
nx.draw_networkx_labels(H, pos, labels=labels, font_size=9)

plt.title("👥 Communautés parmi les top 50 co-auteurs", fontsize=14)
plt.axis("off")
plt.tight_layout()
plt.show()
