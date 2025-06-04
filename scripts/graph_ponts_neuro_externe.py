import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from collections import Counter
from pathlib import Path

# Chargement des chemins
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data_graph"
output_dir = base_dir / "outputs"

# Chargement des fichiers
df_neuro = pd.read_json(data_dir/"dblp_filtered_light.jsonl", lines=True)

# Limiter à 2000 articles non neuro de manière aléatoire
df_non_full = pd.read_json(data_dir/"dblp_non_neuro_filtered_full.jsonl", lines=True)
df_non = df_non_full.sample(n=2000, random_state=42)

#  Fusionner les deux datasets
df_total = pd.concat([df_neuro, df_non])

# Construction du graphe complet
G_total = nx.Graph()
edge_counter = Counter()

for _, row in df_total.iterrows():
    authors = [a["name"] for a in row["authors"] if "name" in a]
    for a1, a2 in combinations(authors, 2):
        edge = tuple(sorted((a1, a2)))
        edge_counter[edge] += 1

for (a1, a2), weight in edge_counter.items():
    G_total.add_edge(a1, a2, weight=weight)

# Identifier les auteurs neuro et non-neuro
auteurs_neuro = set(a["name"] for row in df_neuro["authors"] for a in row if "name" in a)
auteurs_non = set(a["name"] for row in df_non["authors"] for a in row if "name" in a)

#  Identifier les ponts
ponts = []
for a1 in auteurs_neuro:
    if a1 in G_total:
        for voisin in G_total.neighbors(a1):
            if voisin in auteurs_non:
                ponts.append((a1, voisin))

print(f"🔗 {len(ponts)} ponts trouvés entre auteurs neuro et non-neuro.")

# Sous-graphe des ponts
G_ponts = nx.Graph()
G_ponts.add_edges_from(ponts)

# Attributs pour couleurs
for node in G_ponts.nodes():
    if node in auteurs_neuro:
        G_ponts.nodes[node]["type"] = "neuro"
    elif node in auteurs_non:
        G_ponts.nodes[node]["type"] = "non-neuro"
    else:
        G_ponts.nodes[node]["type"] = "inconnu"

colors = {"neuro": "skyblue", "non-neuro": "lightcoral", "inconnu": "gray"}
node_colors = [colors.get(G_ponts.nodes[n]["type"], "gray") for n in G_ponts.nodes()]

# Visualisation
plt.figure(figsize=(14, 10))
pos = nx.spring_layout(G_ponts, seed=42)
nx.draw(G_ponts, pos, node_color=node_colors, node_size=40, edge_color="#cccccc", with_labels=False)

# Labels des nœuds centraux
centrality = nx.degree_centrality(G_ponts)
labels = {n: n for n, c in centrality.items() if c > 0.02}
nx.draw_networkx_labels(G_ponts, pos, labels, font_size=8)

nx.write_gexf(G_ponts, output_dir / "graph_ponts_neuro_externe.gexf")
print("✅ Graphe des ponts sauvegardé dans : graph_ponts_neuro_externe.gexf")
plt.title("🔗 Ponts entre auteurs neurosciences et non-neurosciences")
plt.axis("off")
plt.tight_layout()

# Sauvegarde
plt.savefig(output_dir/"ponts_neuro_externe.png", dpi=300)
print("🖼️ Image sauvegardée dans : ponts_neuro_externe.png")
plt.show()
