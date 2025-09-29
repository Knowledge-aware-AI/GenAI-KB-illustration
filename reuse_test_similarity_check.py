import sqlite3
import random
import os
import pickle
import pandas as pd

os.environ["HF_HOME"] = r"O:\Schule Studium o.o\Master\00_Research Project und Masterarbeit\thesis_code\huggingface\models"
#os.environ["TRANSFORMERS_CACHE"] = r"O:\Schule Studium o.o\Master\00_Research Project und Masterarbeit\thesis_code\huggingface\models\transformers"

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import paraphrase_mining

# ====== CONFIG ======
GPTKB_PATH = "GPTKB/gptkb_v1.5.1.db"
IMG_FOLDER = "scale_test/gen_images"
PICKS_FILE = "scale_test/random_500.pkl"
DF_FILE = "scale_test/entries_500_nosubjects.pkl"
# ====================

# Connect to SQLite
connect_sql = sqlite3.connect(GPTKB_PATH)
cur = connect_sql.cursor()


def extract_entry(subject_uri):
    """Fetch all triples for a subject name (exact or LIKE match)."""
    subject_uri = subject_uri.removesuffix(".png")
    
    # Try exact match
    full_entry = list(cur.execute(
        "SELECT predicate, object FROM gptkb WHERE subject = ?", # "SELECT subject, predicate, object FROM gptkb WHERE subject = ?",
        (subject_uri,)
    ))
    
    # If not found, try LIKE
    if not full_entry:
        subject_uri_like = subject_uri.replace("_", "%")
        full_entry = list(cur.execute(
            "SELECT predicate, object FROM gptkb WHERE subject LIKE ?", # "SELECT subject, predicate, object FROM gptkb WHERE subject LIKE ?",
            (subject_uri_like,)
        ))
    
    if not full_entry:
        return ""
    
    return "\n".join(f"{pred} {obj}" for pred, obj in full_entry) # {subj} {pred} {obj}" for subj, pred, obj in full_entry)


def get_nonempty_random_500(folder_path, save_file=None):
    """Get 500 random image names with non-empty DB entries."""
    folder_list = os.listdir(folder_path)
    chosen = set()
    final_list = []
    
    while len(final_list) < 500:
        candidate = random.choice(folder_list)
        if candidate in chosen:
            continue
        if extract_entry(candidate):  # only accept if non-empty
            final_list.append(candidate)
            chosen.add(candidate)
    
    if save_file:
        with open(save_file, "wb") as f:
            pickle.dump(final_list, f)
    
    return final_list


def build_dataframe(picks):
    """Build DataFrame of subject/entry pairs, replacing empties if needed."""
    data = []
    folder_list = os.listdir(IMG_FOLDER)
    used = set(picks)  # track used so replacements are unique
    
    for pick in picks:
        subject = pick.removesuffix(".png")
        entry = extract_entry(pick)
        
        # If empty, replace
        if not entry:
            replacement = None
            while True:
                candidate = random.choice(folder_list)
                if candidate not in used and extract_entry(candidate):
                    replacement = candidate
                    used.add(candidate)
                    break
            subject = replacement.removesuffix(".png")
            entry = extract_entry(replacement)
        
        data.append({"subject": subject, "entry": entry})
    
    return pd.DataFrame(data)

model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1")

def add_similarity_columns(df, model=model):
    """Find the most similar entry for each row and add it to the DataFrame."""
    paraphrases = paraphrase_mining(
        model, df["entry"].tolist(),
        corpus_chunk_size=499, top_k=1,
        show_progress_bar=True
    )
    
    # Prepare empty columns
    df["most_similar_idx"] = -1
    df["similarity_score"] = 0.0
    df["most_similar_subject"] = ""   # new column for subject name
    
    # Track best matches
    best_match = {}
    for score, i, j in paraphrases:
        if i not in best_match:
            best_match[i] = (j, score)
        if j not in best_match:
            best_match[j] = (i, score)
    
    # Fill DataFrame
    for idx, (match_idx, score) in best_match.items():
        df.at[idx, "most_similar_idx"] = match_idx
        df.at[idx, "similarity_score"] = score
        df.at[idx, "most_similar_subject"] = df.at[match_idx, "subject"]
    
    return df


# ===== Main execution =====

# Load picks or generate new
if os.path.exists(PICKS_FILE):
    with open(PICKS_FILE, "rb") as f:
        picks = pickle.load(f)
else:
    picks = get_nonempty_random_500(IMG_FOLDER, save_file=PICKS_FILE)

# Build DataFrame (with safety replacement for empties)
df = build_dataframe(picks)

# Add similarity columns
df = add_similarity_columns(df)

# Save DataFrame
with open(DF_FILE, "wb") as f:
    pickle.dump(df, f)

df.to_csv("scale_test/similarity_nosubjects.csv", sep=";", index=False, header=True, encoding="utf-8")

# Close DB
connect_sql.close()

# Show first rows
print(df.head())