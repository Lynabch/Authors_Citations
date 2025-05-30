import pandas as pd

# 📁 Chemin du fichier JSONL nettoyé
input_file = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_cleaned_step1.jsonl"

# 📥 Charger les données JSONL
df = pd.read_json(input_file, lines=True)

print(f"🔍 Nombre total d'articles : {len(df)}")

# 🧹 Filtrer les publications après 2000
df = df[df["year"] > 2000]
print(f"✅ Articles publiés après 2000 : {len(df)}")

# 🧩 Filtrer uniquement les articles de type 'Journal' ou 'Conference'
df = df[df["doc_type"].isin(["Journal", "Conference"])]
print(f"✅ Articles de type 'Journal' ou 'Conference' : {len(df)}")

# 🎯 Sélectionner les colonnes utiles pour les nœuds du graphe
colonnes_utiles = ["id", "title", "year", "venue", "n_citation", "abstract", "authors", "doc_type"]
df = df[colonnes_utiles]

# 👁️ Exemple d'aperçu :
print("\n📌 Exemple d’article :")
print(df.iloc[0])

# 💾 Enregistrer les nœuds filtrés dans un nouveau fichier
output_file = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_nodes_after2000.jsonl"
df.to_json(output_file, orient="records", lines=True)

print(f"✅ Nœuds sauvegardés dans : {output_file}")
