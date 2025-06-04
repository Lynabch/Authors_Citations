import pandas as pd
import networkx as nx
from collections import defaultdict
from pathlib import Path
#  Définir les chemins
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data_graph"
output_dir = base_dir / "outputs"

# Charger le graphe
gexf_file = data_dir/ "graph_neuro_no_pagerank.gexf"
G = nx.read_gexf(gexf_file)

# Charger les articles
articles_file = data_dir / "dblp_filtered_light.jsonl"
df_articles = pd.read_json(articles_file, lines=True)

# Extraire les communautés
partition = nx.get_node_attributes(G, "community")

# Grouper les nœuds par communauté
communities = defaultdict(list)
for node, comm in partition.items():
    communities[comm].append(node)

# Associer les titres aux communautés
articles_by_comm = defaultdict(list)
for _, row in df_articles.iterrows():
    authors = [a["name"] for a in row["authors"] if "name" in a]
    # Chercher à quelle communauté appartient au moins un auteur
    comms = set(partition.get(a) for a in authors if a in partition)
    for comm in comms:
        if pd.notnull(row["title"]):
            articles_by_comm[comm].append(row["title"])

# Calcul stats + auteurs + titres
stats = []
for comm, nodes in communities.items():
    subgraph = G.subgraph(nodes)
    n = subgraph.number_of_nodes()
    m = subgraph.number_of_edges()
    densite = nx.density(subgraph)
    degre_moyen = sum(dict(subgraph.degree()).values()) / n if n > 0 else 0
    auteurs = ", ".join(sorted(nodes))
    titres = " / ".join(articles_by_comm[comm][:10])  # Limiter à 10 titres pour lisibilité
    stats.append({
        "Communauté": comm,
        "Nb auteurs": n,
        "Nb liens internes": m,
        "Densité": round(densite, 3),
        "Degré moyen": round(degre_moyen, 2),
        "Auteurs": auteurs,
        "Titres (extraits)": titres
    })

# Export Excel
df_stats = pd.DataFrame(stats).sort_values("Nb auteurs", ascending=False)
excel_file = output_dir / "stats_communautes_neuro.xlsx"
df_stats.to_excel(excel_file, index=False)
print(f"✅ Export enrichi avec titres sauvegardé dans : {excel_file}")
