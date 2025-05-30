import pandas as pd

# 📥 Charger les données JSONL après 2000
input_file = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_nodes_after2000.jsonl"
df = pd.read_json(input_file, lines=True)

# ✂️ Garder uniquement les articles avec titre non nul et liste d'auteurs valide
df = df[df["title"].apply(lambda x: isinstance(x, str) and len(x.strip()) > 5)]
df = df[df["authors"].apply(lambda x: isinstance(x, list) and 2 <= len(x) <= 10)]

# Supprimer les auteurs dont le nom est vide ou incomplet
def clean_authors(authors):
    return [a for a in authors if "name" in a and len(a["name"].split()) >= 2]
df["authors"] = df["authors"].apply(clean_authors)
df = df[df["authors"].apply(lambda x: len(x) > 1)]

# 🧠 Mots-clés neuroscience
neuro_keywords = ["neuro", "brain", "cortex", "synapse", "neuronal", "neural", "cognitive", "EEG", "fMRI"]

# 🔍 Exclure les articles liés à la neuroscience
def is_non_neuro(text):
    if not isinstance(text, str):
        return True
    return not any(kw in text.lower() for kw in neuro_keywords)

df = df[df["title"].apply(is_non_neuro) & df["abstract"].apply(is_non_neuro)]

# Trier par nombre de citations (facultatif)
df = df.sort_values("n_citation", ascending=False)

# 💾 Export sans limitation
output_file = "C:/Users/baouc/Documents/GRAPH_DATA/data_graph/dblp_non_neuro_filtered_full.jsonl"
df.to_json(output_file, orient="records", lines=True)

print(f"✅ Articles non neuroscience filtrés (sans limite) sauvegardés dans : {output_file}")
print(f"🔢 Nombre total conservé : {len(df)}")
