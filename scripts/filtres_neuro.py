import pandas as pd
from pathlib import Path

# Fichier du graphe de co-auteurs
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data_graph"
output_dir = base_dir / "outputs"
# Chargement du fichier JSONL déjà pré-filtré (après 2000, etc.)
input_file = data_dir/"dblp_nodes_after2000.jsonl"
df = pd.read_json(input_file, lines=True)

# Filtres légers pour conserver un maximum d'articles valides
# Garder les articles avec un nombre d'auteurs raisonnable (2 à 10)
df = df[df["authors"].apply(lambda x: isinstance(x, list) and 2 <= len(x) <= 10)]

# Nettoyer légèrement les noms d'auteurs (au moins deux mots dans le nom)
def clean_authors(authors):
    return [a for a in authors if "name" in a and len(a["name"].split()) >= 2]

df["authors"] = df["authors"].apply(clean_authors)

# Ne garder que les articles avec encore au moins 2 auteurs valides
df = df[df["authors"].apply(lambda x: len(x) > 1)]

# Mots-clés liés aux neurosciences
neuro_keywords = ["neuro", "brain", "cortex", "synapse", "neuronal", "neural", "cognitive", "EEG", "fMRI","nervous system", "hippocampus","neuroscience"]

# Fonction de filtrage thématique sur le titre ou le résumé
def contains_neuro_keywords(text):
    if not isinstance(text, str):
        return False
    return any(kw in text.lower() for kw in neuro_keywords)

# Filtrer les articles contenant des mots-clés neurosciences
df = df[df["title"].apply(contains_neuro_keywords) | df["abstract"].apply(contains_neuro_keywords)]

# Trier par nombre de citations et limiter à 2000 articles
df = df.sort_values("n_citation", ascending=False).head(2000)

print(f"🔢 Nombre d'articles filtrés sur la thématique neuroscience : {len(df)}")
# 💾 Enregistrer dans un nouveau fichier JSONL
output_file = output_dir/"dblp_filtered_light.jsonl"
df.to_json(output_file, orient="records", lines=True)

print(f"✅ Fichier filtré sauvegardé dans : {output_file}")
print(f"🔢 Nombre total d'articles conservés : {len(df)}")
