import pandas as pd
import networkx as nx
from itertools import combinations
from collections import Counter
import community as community_louvain
import matplotlib.pyplot as plt

# 📥 1. Chargement des données
input_file = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_nodes_after2000.jsonl"
df = pd.read_json(input_file, lines=True)

# ✂️ 2. Filtres avancés pour optimiser les performances

# Garder seulement les colonnes utiles
df = df[["title", "authors", "year", "venue", "n_citation"]]

# Supprimer les articles avec auteurs vides ou trop nombreux (bruits)
df = df[df["authors"].apply(lambda x: isinstance(x, list) and 2 <= len(x) <= 10)]

# Supprimer les auteurs ambigus (initiales uniquement, noms incomplets)
def clean_authors(authors):
    return [a for a in authors if "name" in a and len(a["name"].split()) >= 2 and "." not in a["name"]]

df["authors"] = df["authors"].apply(clean_authors)

# Retirer les lignes avec <2 auteurs valides après nettoyage
df = df[df["authors"].apply(lambda x: len(x) > 1)]

# Garder uniquement les publications de conférences réputées (optionnel)
journals = ["ICML", "NeurIPS", "AAAI", "KDD", "CVPR", "ACL", "EMNLP"]
df = df[df["venue"].isin(journals)]

# Trier par nombre de citations (impact) et prendre les 2000 premiers pour test
df = df.sort_values("n_citation", ascending=False).head(2000)

# 📊 3. Construction du graphe de co-auteurs
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

# 🧠 4. Clustering Louvain
partition = community_louvain.best_partition(G)
nx.set_node_attributes(G, partition, 'community')

# 📈 5. Centralités
degree_centrality = nx.degree_centrality(G)
pagerank = nx.pagerank(G)

nx.set_node_attributes(G, degree_centrality, 'degree_centrality')
nx.set_node_attributes(G, pagerank, 'pagerank')

# 🎨 6. Visualisation d’un sous-graphe (top 200 auteurs par centralité)
top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:200]
subgraph = G.subgraph([n for n, _ in top_nodes])

pos = nx.spring_layout(subgraph)
node_color = [partition[n] for n in subgraph.nodes()]
node_size = [degree_centrality[n]*3000 for n in subgraph.nodes()]

plt.figure(figsize=(15, 10))
nx.draw(subgraph, pos, with_labels=True, node_color=node_color, node_size=node_size,
        edge_color="#ccc", font_size=8)
plt.title("🔗 Graphe de co-auteurs (Top 200 nœuds)")
plt.show()

# 💾 7. Export optionnel des résultats
top_authors = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:20]
df_top = pd.DataFrame(top_authors, columns=["Auteur", "PageRank"])
df_top.to_csv("C:/Users/baouc/Documents/GRAPH_DATA/data_graph/top_auteurs.csv", index=False)
print("📦 Résultats exportés dans 'top_auteurs.csv'")
