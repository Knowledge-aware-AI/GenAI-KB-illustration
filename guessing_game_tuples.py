import random
import os
import openai
from openai import OpenAI
import time
import base64
import pandas as pd
import sqlite3

GPTKB_PATH = "GPTKB/gptkb_v1.5.1.db"

# Connect to SQLite
connect_sql = sqlite3.connect(GPTKB_PATH)
cur = connect_sql.cursor()

def guessing_game(entry, guess_options, retries=3):
    content = (
        "Let's play a guessing game! "
        f"These are some lines of a knowledge base entry: {entry}"
        "Guess which of these 4 subjects it is. "
        f"These are the possible subjects: {guess_options}. "
        "Respond with only the subject you guessed and nothing more."
    )

    for attempt in range(retries):
        try:
            response = client_tu.chat.completions.create(
                messages=[{"role":"user","content":content}],
                model=model_name
                )
            
            return response.choices[0].message.content
        except openai.RateLimitError:
            wait_time = min(2 ** attempt, 60)
            print(f"Rate limit hit. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        except (openai.InternalServerError, openai.AuthenticationError) as e:
            print(f"{e}")
            print("Can't reach server, trying again in 10 minutes.")
            time.sleep(600)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    return None

def get_guess_options(true_subject, subjects):
    randomized = []
    while not randomized:
        sample = random.sample(subjects, k=3)
        if true_subject not in sample:
            randomized = sample

    options = [true_subject] + randomized

    random.shuffle(options)

    return options

def get_entry(subject_uri, limit_count, cur=cur):
    """Fetch all triples for a subject name (exact or LIKE match)."""
    subject_uri = subject_uri.removesuffix(".png")
    
    # Try exact match
    full_entry = list(cur.execute(
        f"SELECT predicate, object FROM gptkb WHERE subject = ? LIMIT {int(limit_count)}", # "SELECT subject, predicate, object FROM gptkb WHERE subject = ?",
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
    
    return "\n".join(f"{pred} {obj}" for pred, obj in full_entry)

#set scads.ai API key
my_api_key = os.environ.get("TU_API_KEY")
client_tu = OpenAI(base_url="https://llm.scads.ai/v1",api_key=my_api_key)

# Find model with "llama" in name
for model in client_tu.models.list().data:
    #print(model.id)  
    model_name = model.id
    if "Llama4" in model_name:
        break


# Load pickle file
file_path3 = "scale_test/entries_500_nosubjects.pkl"
# Load the DataFrame from pickle
df = pd.read_pickle(file_path3)

# Extract "subject" column into rnd3_subjects list, formatted like your example
rnd3_subjects = [
    str(subj).strip()
    for subj in df["subject"]
    if str(subj).strip()
]
# Extract "most_similar_subject" column into rnd3_sim_subj list, formatted like your example
rnd3_sim_subj = [
    str(subj).strip()
    for subj in df["most_similar_subject"]
    if str(subj).strip()
]

one = []
two = []
three = []
rnd3_entries = [one, two, three]

for name in rnd3_subjects:
    for j, count in enumerate([1,2,3]):
        rnd3_entries[j].append(get_entry(name,count))
print("Finished grabbing all entries!")
print("0-0:", rnd3_entries[0][0])
print("1-0:", rnd3_entries[1][0])
print("2-0:", rnd3_entries[2][0])

subjects = [rnd3_subjects,
            rnd3_subjects,
            rnd3_subjects]
image_path = [r"scale_test/gen_images/",
              r"scale_test/gen_images/",
              r"scale_test/gen_images/"]
gen_variant = ["1_Tuples",
               "2_Tuples",
               "3_Tuples"]
entry_counter = [0,
                 1,
                 2]

for i in range(6):
    for variant in range(len(subjects)):
        text = []
        
        save_path = image_path[variant].replace("gen_images/","")
        saved_path = f"{save_path}guessing_game_lv2_{gen_variant[variant]}_0{i}.txt"
        
        if os.path.isfile(saved_path):
            continue

        for count,_ in enumerate(subjects[variant]):
            #subject = parse_file_name(file)
            
            if (variant % 2) == 0:
                subject = rnd3_subjects[count]
            else:
                subject = rnd3_sim_subj[count]
            
            guess_options = get_guess_options(subject, subjects[variant])
            
            guess = guessing_game(rnd3_entries[entry_counter[variant]][count], guess_options)
            print(f"Guess made for {subject}.")
            
            text.append(f"{subject}: {guess_options} --- {guess}")
            time.sleep(1)
        
        # Save to file
        with open(saved_path, "w", encoding="utf-8") as txt_file:
            for subj in text:
                txt_file.write(subj + "\n")
        
        print(f"Saved TXT-file as \"{saved_path}\".")

# Close DB
connect_sql.close()