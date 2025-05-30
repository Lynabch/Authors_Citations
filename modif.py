import json
import os
import ijson

# 📍 Chemins des fichiers
original_path = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_v14.json"
cleaned_json_path = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_v14_cleaned.json"
output_path = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_cleaned_step1.jsonl"

# 🔹 Étape 1 : Extraire le vrai JSON (de [ à ])
with open(original_path, "rb") as f:
    content = f.read()
    start = content.find(b"[")
    end = content.rfind(b"]") + 1
    if start == -1 or end == -1:
        raise ValueError("❌ Impossible de détecter correctement la structure du JSON.")
    cleaned_content = content[start:end]

# 🔹 Sauvegarde dans un nouveau fichier JSON bien formé
with open(cleaned_json_path, "wb") as f:
    f.write(cleaned_content)

print(f"✅ Fichier nettoyé temporaire créé : {cleaned_json_path}")

# 🔹 Étape 2 : Lecture avec ijson + filtrage + nettoyage
champs_utiles = {"id", "title", "year", "venue", "abstract", "authors", "n_citation", "doc_type"}
accepted_doc_types = {"Journal", "Conference"}

with open(cleaned_json_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    count = 0
    for article in ijson.items(infile, "item"):
        year = article.get("year")
        doc_type = article.get("doc_type")
        n_citation = article.get("n_citation", 0)

        # 🔸 Condition de filtrage
        if year and int(year) > 2000 and doc_type in accepted_doc_types and n_citation > 0:
            # Ne garder que les champs utiles
            cleaned = {key: article[key] for key in champs_utiles if key in article}

            # Nettoyage des auteurs : suppression de l'ID
            if "authors" in cleaned:
                for author in cleaned["authors"]:
                    author.pop("id", None)

            # Écriture dans le fichier .jsonl
            outfile.write(json.dumps(cleaned) + "\n")
            count += 1

print(f"✅ {count} articles filtrés et nettoyés enregistrés dans : {output_path}")
