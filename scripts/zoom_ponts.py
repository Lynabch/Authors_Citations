import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.patches import Patch

# 📁 Définir les chemins de base
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data_graph"
output_dir = base_dir / "outputs"

# 📥 Charger le graphe des ponts sauvegardé
G = nx.read_gexf(output_dir / "graph_ponts_neuro_externe.gexf")

# 🔍 Sélectionner les 30 auteurs non-neuro les plus connectés
top_non_neuro = [
    (n, deg) for n, deg in G.degree()
    if G.nodes[n].get("type") == "non-neuro"
]
top_non_neuro = sorted(top_non_neuro, key=lambda x: x[1], reverse=True)[:30]
top_non_neuro_nodes = [n for n, _ in top_non_neuro]

# ➕ Ajouter les voisins de type "neuro"
voisins_neuro = []
for n in top_non_neuro_nodes:
    voisins_neuro += [
        v for v in G.neighbors(n)
        if G.nodes[v].get("type") == "neuro"
    ]

# 🧱 Construire le sous-graphe
nodes_to_keep = list(set(top_non_neuro_nodes + voisins_neuro))
H = G.subgraph(nodes_to_keep).copy()

# 🎨 Couleurs des nœuds
colors = {"neuro": "skyblue", "non-neuro": "lightcoral", "inconnu": "gray"}
node_colors = [colors.get(H.nodes[n].get("type", "inconnu"), "gray") for n in H.nodes()]
pos = nx.spring_layout(H, seed=42, k=0.5)

# 🖼️ Affichage
plt.figure(figsize=(12, 9))
nx.draw_networkx_nodes(H, pos, node_color=node_colors, node_size=600)
nx.draw_networkx_edges(H, pos, alpha=0.4)
nx.draw_networkx_labels(H, pos, font_size=8)

# 🗂️ Légende
legend_elements = [
    Patch(facecolor="skyblue", label="Neuro"),
    Patch(facecolor="lightcoral", label="Non-neuro")
]
plt.legend(handles=legend_elements, loc="best")

plt.title(" Zoom : Top 30 auteurs non-neuro connectés à des auteurs neuro")
plt.axis("off")
plt.tight_layout()

# 💾 Sauvegarde de l'image
plt.savefig(output_dir / "zoom_top_externes_mixtes.png", dpi=300)
plt.show()
