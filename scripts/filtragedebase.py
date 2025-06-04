import json
import ijson
import pandas as pd
from pathlib import Path
# Fichiers d'entrée / sortie
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data_graph"
output_dir = base_dir / "outputs"

cleaned_json_path = data_dir / "dblp_nodes_cleaned.jsonl"
filtered_output_path = data_dir / "dblp_filtered_neuro.jsonl"

# Champs utiles
champs_utiles = {"id", "title", "year", "venue", "abstract", "authors", "n_citation", "doc_type", "references"}
accepted_doc_types = {"Journal", "Conference"}

# Lecture ligne à ligne avec ijson
temp_filtered_articles = []

with open(cleaned_json_path, "r", encoding="utf-8") as infile:
    for article in ijson.items(infile, "item"):
        year = article.get("year")
        doc_type = article.get("doc_type")
        n_citation = article.get("n_citation", 0)

        if year and int(year) > 2000 and doc_type in accepted_doc_types and n_citation > 0:
            cleaned = {key: article[key] for key in champs_utiles if key in article}

            # Nettoyage des auteurs
            if "authors" in cleaned:
                authors = [a for a in cleaned["authors"] if "name" in a and len(a["name"].split()) >= 2]
                if 2 <= len(authors) <= 10:
                    cleaned["authors"] = authors
                    if cleaned.get("title") and len(cleaned["title"].strip()) > 5:
                        temp_filtered_articles.append(cleaned)

print(f"✅ {len(temp_filtered_articles)} articles retenus après filtrage.")

# 💾 Export vers JSONL
df = pd.DataFrame(temp_filtered_articles)
colonnes_utiles = ["id", "title", "year", "venue", "n_citation", "abstract", "authors", "doc_type", "references"]
df = df[colonnes_utiles]

print("\n📌 Exemple d’article :")
print(df.iloc[0])

df.to_json(filtered_output_path, orient="records", lines=True)
print(f"✅ Fichier final sauvegardé dans : {filtered_output_path}")
