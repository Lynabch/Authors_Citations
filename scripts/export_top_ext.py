import pandas as pd
import networkx as nx
from pathlib import Path

# 📁 Répertoires
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data_graph"
output_dir = base_dir / "outputs"

# 📥 Charger le graphe
G = nx.read_gexf(output_dir / "graph_ponts_neuro_externe.gexf")

# 📥 Charger les articles non neuro
df_non = pd.read_json(data_dir / "dblp_non_neuro_filtered_full.jsonl", lines=True)

# 🔍 Top 30 auteurs non-neuro les plus connectés
top_non_neuro = sorted(
    [(n, deg) for n, deg in G.degree() if G.nodes[n].get("type") == "non-neuro"],
    key=lambda x: x[1], reverse=True
)[:30]
top_names = [n for n, _ in top_non_neuro]

# 📊 Chercher les articles liés à ces auteurs
resultats = []

for _, row in df_non.iterrows():
    article_auteurs = [a["name"] for a in row["authors"] if "name" in a]
    intersect = set(article_auteurs).intersection(top_names)

    if intersect:
        resultats.append({
            "Auteurs dans top 30": ", ".join(intersect),
            "Co-auteurs": ", ".join(article_auteurs),
            "Titre": row["title"],
            "Année": row.get("year"),
            "Nb de citations": row.get("n_citation", 0)
        })

# 📁 Exporter vers Excel
df_resultats = pd.DataFrame(resultats)
excel_path = output_dir / "top_30_externes_articles.xlsx"
df_resultats.to_excel(excel_path, index=False)

print(f"✅ Fichier Excel exporté : {excel_path}")
