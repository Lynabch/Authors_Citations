import pandas as pd
import json

# Fichiers
all_articles_path = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_nodes_after2000.jsonl"
neuro_articles_path = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_filtered_light.jsonl"
output_file = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_non_neuro_filtered_full.jsonl"

# Chargement des IDs neuroscientifiques à exclure
neuro_ids = set()
with open(neuro_articles_path, "r", encoding="utf-8") as f:
    for line in f:
        article = json.loads(line)
        neuro_ids.add(article["id"])

# Charger tous les articles
df = pd.read_json(all_articles_path, lines=True)

print(f"🔍 Articles initiaux : {len(df)}")

# Nettoyage minimal
df = df[df["title"].apply(lambda x: isinstance(x, str) and len(x.strip()) > 5)]
df = df[df["authors"].apply(lambda x: isinstance(x, list) and 2 <= len(x) <= 10)]

def clean_authors(authors):
    return [a for a in authors if "name" in a and len(a["name"].split()) >= 2]
df["authors"] = df["authors"].apply(clean_authors)
df = df[df["authors"].apply(lambda x: len(x) > 1)]

# Exclure tous les articles identifiés comme neurosciences
df = df[~df["id"].isin(neuro_ids)]
print(f"✅ Après exclusion des articles neuro : {len(df)}")

# Re-filtrer par absence de termes neuro (sécurité)
neuro_keywords = ["neuro", "brain", "cortex", "synapse", "neuronal", "neural", "cognitive", "EEG", "fMRI"]
def is_non_neuro(text):
    if not isinstance(text, str):
        return True
    return not any(kw in text.lower() for kw in neuro_keywords)

df = df[df["title"].apply(is_non_neuro) & df["abstract"].apply(is_non_neuro)]
print(f"✅ Après contrôle mot-clé neuro : {len(df)}")

# Thématiques "scientifiques" / biomédicales
science_keywords = [
    "nature", "science", "ieee", "acm", "elsevier", "springer", "plos", "jama", "lancet", "cell", "pnas",
    "medical", "biological", "biomedicine", "health", "clinical", "genetics", "immunology", "pharmacology",
    "toxicology", "epidemiology", "pathology", "physiology", "biochemistry", "molecular biology",
    "biophysics", "psychology", "cognitive science", "behavioral science"
]

# Appliquer le filtre via le champ venue.raw si dispo
def match_science_keywords(venue):
    if isinstance(venue, dict):
        venue = venue.get("raw", "")
    return any(kw in str(venue).lower() for kw in science_keywords)

df = df[df["venue"].apply(match_science_keywords)]
print(f"✅ Articles non neuro mais scientifiques conservés : {len(df)}")

# Sauvegarde
df.to_json(output_file, orient="records", lines=True)
print(f"💾 Fichier sauvegardé dans : {output_file}")
