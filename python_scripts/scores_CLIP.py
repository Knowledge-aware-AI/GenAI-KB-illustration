import PIL
import torch
import os
from transformers import CLIPProcessor, CLIPModel
import torch.nn.functional as F
import pandas as pd

# Load model once globally
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_id = "zer0int/LongCLIP-L-Diffusers"   # used for larger context window than 77)
model = CLIPModel.from_pretrained(model_id).to(device)
processor = CLIPProcessor.from_pretrained(model_id)

def get_clip_score(score_image, score_gt):
    # Process each image individually
    inputs_img1 = processor(images=score_image, return_tensors="pt").to(device)
    inputs_img2 = processor(images=score_gt, return_tensors="pt").to(device)

    with torch.no_grad():
        img1_features = model.get_image_features(**inputs_img1)
        img2_features = model.get_image_features(**inputs_img2)

        # Normalize embeddings
        img1_features = F.normalize(img1_features, p=2, dim=1)
        img2_features = F.normalize(img2_features, p=2, dim=1)

        # Compute cosine similarity
        similarity = torch.matmul(img1_features, img2_features.T).item()

    # Scale from [-1, 1] to [0, 100]
    return round(((similarity + 1) / 2) * 100, 2)

def read_first_line(file):
     with open(file, 'rt') as fd:
         first_line = fd.readline()
     return first_line

def find_file_by_subject(subject_name, folder):
    for f in os.listdir(folder):
        name, ext = os.path.splitext(f)
        if name == subject_name:
            return f
    return None  # not found

gen_image_path = "gen_images"
simple_path = "gen_images_simple"
medium_path = "gen_images_medium"
complex_path = "gen_images_complex"

####### following sets can be used to run script once for multiple folders ############
image_prefix = ["scale_test/"]
image_suffix = ["/"]
gt_prefix = ["scale_test/"]

ground_truth_path = "ground_truth/"

##### FOR RANDOMLY CHOSEN SUBJECTS (Random dataset)
file_path = "sampled_subjects.txt"

# Load subjects into a list, replacing spaces with underscores
with open(file_path, "r", encoding="utf-8") as f:
    rnd_subjects = [line.strip().replace(" ", "_").replace(":", "").replace(",", "") for line in f if line.strip()]
    
##### FOR RANDOMLY CHOSEN SUBJECTS (New Random dataset)
file_path2 = "new/sampled_subjects.txt"

# Load subjects into a list, replacing spaces with underscores
with open(file_path2, "r", encoding="utf-8") as f:
    rnd2_subjects = [line.strip().replace(" ", "_").replace(":", "").replace(",", "") for line in f if line.strip()]
    
##### FOR SCALE TEST SUBJECTS (Scale Test dataset)
file_path3 = "scale_test/entries_500_nosubjects.pkl"
# Load the DataFrame from pickle
df = pd.read_pickle(file_path3)

# Extract "subject" column into rnd3_subjects list
rnd3_subjects = [
    str(subj).strip()
    for subj in df["subject"]
    if str(subj).strip()
]
# Extract "most_similar_subject" column into rnd3_sim_subj list
rnd3_sim_subj = [
    str(subj).strip()
    for subj in df["most_similar_subject"]
    if str(subj).strip()
]
# Extract similarity scores
rnd3_scores = [
    float(score) for score in df["similarity_score"]
]

# The handpicked subjects referred to as Regular dataset
chosen_subjects = [
    'Vatican_City', 'Miami', 'Vienna', 'Columbus', 'San_Marino',
    'Kansas_City', 'Sacramento', 'Fresno', 'Amsterdam', 'Brussels',
    'Manama', 'Rabat', 'Kuala_Lumpur', 'Manila', 'Dubai',
    'Nairobi', 'Singapore', 'Bangkok', 'Dhaka', 'Cairo',

    'Apostolic_Palace', 'Freedom_Tower', 'St._Stephen%27s_Cathedral',
    'Scioto_Mile', 'Guaita_Fortress', 'The_Folly_Theater', 'Tower_Bridge',
    'Fresno_Water_Tower', 'Dam_Square', 'Manneken_Pis', 'Bahrain_Fort',
    'Mausoleum_of_Mohammed_V', 'Chinatown', 'Intramuros', 'Burj_Khalifa',
    'Bomas_of_Kenya', 'Botanic_Gardens', 'Central_World', 'Jatiyo_Sangsad_Bhaban',
    'Al-Azhar_Mosque',

    'The_J._M._Smucker_Company', 'Fujifilm_Baltic_SIA', 'Suncor_Energy',
    'Symington_Family_Estates', 'United_States_Rubber_Company', 'Snap_Inc.',
    'Johnson_%26_Johnson_Consumer_Health', 'B._Braun_Melsungen_AG', 'Daler-Rowney',
    'Luxottica_Group', 'Unity_Technologies', 'Marvelous_Entertainment',
    'American_Tobacco_Company', 'Rocket_Lab_Ltd.', 'UXPin%2C_Inc.',
    'Sony_Corporation', 'Tyco_Electronics', 'Tory_Burch_LLC',
    'Gap%2C_Inc.', 'Furukawa_Co.%2C_Ltd.',

    'butter', 'film', 'natural_gas', 'port', 'footwear',
    'Bitmoji', 'health_services', 'medical_devices', 'canvas',
    'sunglasses', 'Unity', 'video_games', 'tobacco', 'Electron_rocket',
    'UXPin', 'music', 'sensors', 'accessories', 'clothing',
    'Telecommunications',

    'Maya_Widmaier-Picasso', 'Edgar_Allan_Poe', 'Garry_Kasparov',
    'Mary_Wortley_Montagu', 'Johann_Wolfgang_von_Kempelen', 'Wright_brothers',
    'Albert_Einstein', 'Robert_Knox', 'Hitler', 'Ada_Lovelace',
    'M._Carey_Thomas', 'Roberta_Wright_Mc_Cain', 'Piotr_Hofma%C5%84ski',
    'Linus_Yale_Jr.', 'Bessie_Blount', 'Pedro_Paix%C3%A3o',
    'William_C._Gorgas_Jr.', 'Richard_Fleeshman', 'Rushanara_Ali',
    'Zorion_Eguileor',

    'Miss_Peregrine%27s_Peculiar_Children', 'Dummies_series', 'Discworld',
    'James_Bond_Novels', 'Wen_Xuan', 'The_Secrets_of_the_Immortal_Nicholas_Flamel',
    'Bridgewater_Treatises', 'Les_Rougon-Macquart', 'The_Art_of_Computer_Programming',
    'Principia_Mathematica', 'Winnetou', 'Jip_and_Janneke',
    'Mc_Guffey_Readers', 'Voyages_Extraordinaires', 'American_Guide_Series',
    'Lang%27s_Fairy_Books', 'The_Rover_Boys', 'Doctor_Dolittle',
    'Harvard_Classics_series', 'The_Witcher'
]

subjects = [rnd3_subjects]

for version in range(len(image_prefix)):
    all_images = os.listdir(f"{image_prefix[version]}{gen_image_path}{image_suffix[version]}")
    ground_truth = os.listdir(f"{gt_prefix[version]}{ground_truth_path}")

    prompt_types = ['', 'Complex ', 'Medium ', 'Simple ']
    CLIP_names = ['Entity']
    CLIP_scores = ['CLIP Scores']
    Sim_scores = ['Similarity Score']

    try:
        for i, img_name in enumerate(all_images):
            gt_name = ground_truth[i // 3]  # careful: assumes same order!
            true_name, _ = img_name.rsplit(".", 1)
            #true_name = subj_name

            type_indicator = 0  # i % 3
            name_counter = i    # // 3
            prompt_type = prompt_types[type_indicator]

            CLIP_names.append(f"{prompt_type}{true_name}")

            gen_path = f"{image_prefix[version]}{gen_image_path}{image_suffix[version]}{img_name}"
            gt_path = f"{gt_prefix[version]}{ground_truth_path}{gt_name}" 
            
            if version == 3:  # exchange for whichever index the version with simulated reuse for the Large Scale subset has
                # Find the actual filenames by subject name
                sim_file = find_file_by_subject(rnd3_sim_subj[i], f"{image_prefix[version]}{gen_image_path}{image_suffix[version]}")
                gt_file = find_file_by_subject(rnd3_subjects[i], f"{gt_prefix[version]}{ground_truth_path}")

                if not sim_file or not gt_file:
                    print(f"Could not find files for {rnd3_subjects[i]} / {rnd3_sim_subj[i]}")
                    continue

                gen_path = f"{image_prefix[version]}{gen_image_path}{image_suffix[version]}{sim_file}"
                gt_path = f"{gt_prefix[version]}{ground_truth_path}{gt_file}"
            
            print(f"Opening generated image: {gen_path}")
            try:
                with PIL.Image.open(gen_path) as img:
                    img.load()
                print("Generated image loaded.")
            except Exception as e:
                print(f"Could not open generated image {gen_path}: {e}")
                continue

            print(f"Opening ground truth image: {gt_path}")
            try:
                with PIL.Image.open(gt_path) as gt:
                    gt.load()
                print("Ground truth image loaded.")
            except Exception as e:
                print(f"Could not open ground truth image {gt_path}: {e}")
                continue

            #print(f"Scoring {subj_name} vs {rnd3_sim_subj[i]}")
            try:
                with PIL.Image.open(gen_path) as img, PIL.Image.open(gt_path) as gt:
                    clip_score = get_clip_score(img, gt)
                print(f"Done scoring {img_name}, score={clip_score}")
                CLIP_scores.append(clip_score)
                #Sim_scores.append(rnd3_scores[i])   # uncomment if reuse simulation for Large Scale subset is done
            except Exception as e:
                print(f"Error scoring {img_name}: {e}")
                CLIP_scores.append("ERROR")
                Sim_scores.append("ERROR")  # keep alignment

            print("Current CLIP_names:", CLIP_names)
            print("Current CLIP_scores:", CLIP_scores)

    finally:
        save = image_suffix[version][0:-1]
        out_file = f"{image_prefix[version]}CLIP_scores{save}.csv"
        print(f"Saving results to {out_file} ...")

        df_out = pd.DataFrame(list(zip(CLIP_names, CLIP_scores)))#, Sim_scores)))  # readd Sim_scores if simulated reuse for Large Scale subset is done
        df_out.to_csv(out_file, sep=";", index=False, header=False, encoding="utf-8")

        print("Saved CLIP-Score.")
