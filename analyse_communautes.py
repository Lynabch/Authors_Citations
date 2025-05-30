import pandas as pd
import networkx as nx
from collections import defaultdict

# 📥 Charger graphe
G = nx.read_gexf("C:/Users/baouc/Documents/GRAPH_DATA/data_graph/graph_neuro_no_pagerank.gexf")

# 📥 Charger les articles utilisés pour construire le graphe
df_articles = pd.read_json("C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_filtered_light.jsonl", lines=True)

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
output_file = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/stats_communautes_neuro.xlsx"
df_stats.to_excel(output_file, index=False)
print(f"✅ Export enrichi avec titres sauvegardé dans : {output_file}")
