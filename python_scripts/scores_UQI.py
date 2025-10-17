import sewar
import PIL
import os
import numpy as np

def get_uqi_score(score_ground_truth, score_image):
    #make sure the images have the same channels
    score_image = score_image.convert("RGB")
    score_ground_truth = score_ground_truth.convert("RGB")
    
    #crop images to size of the smaller image
    target_size = (min(score_image.width, score_ground_truth.width), min(score_image.height, score_ground_truth.height))
    img_cropped = score_image.crop((0, 0, target_size[0], target_size[1]))
    control_cropped = score_ground_truth.crop((0, 0, target_size[0], target_size[1]))
    
    #make images numpy-arrays so sewar can use them
    np_score_ground_truth = np.array(control_cropped)
    np_score_image = np.array(img_cropped)
    
    #calculate the UQI score between the ground truth and the generated image
    uqi = sewar.full_ref.uqi(np_score_ground_truth, np_score_image, ws=8)
    
    return uqi

def read_first_line(file):
     with open(file, 'rt') as fd:
         first_line = fd.readline()
     return first_line


simple_path = "gen_images_simple/"
medium_path = "gen_images_medium/"
complex_path = "gen_images_complex/"

ground_truth_path = "ground_truth/"

##### FOR RANDOMLY CHOSEN SUBJECTS #######
file_path = "sampled_subjects.txt"

# Load subjects into a list, replacing spaces with underscores
with open(file_path, "r", encoding="utf-8") as f:
    rnd_subjects = [line.strip().replace(" ", "_").replace(":", "") for line in f if line.strip()]
    
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

subjects = [chosen_subjects]
image_prefix = [""]
gt_prefix = [""]

for version in range(len(subjects)):
    images_simple = os.listdir(f"{image_prefix[version]}{simple_path}")
    simple = []
    images_medium = os.listdir(f"{image_prefix[version]}{medium_path}")
    medium = []
    images_complex = os.listdir(f"{image_prefix[version]}{complex_path}")
    complex = []

    ground_truth = os.listdir(f"{gt_prefix[version]}{ground_truth_path}")
    truth = []

    for img in images_simple:
        simple.append(PIL.Image.open(f"{image_prefix[version]}{simple_path}{img}"))
    for img in images_medium:
        medium.append(PIL.Image.open(f"{image_prefix[version]}{medium_path}{img}"))    
    for img in images_complex:
        complex.append(PIL.Image.open(f"{image_prefix[version]}{complex_path}{img}"))
            
    for true in ground_truth:
        truth.append(PIL.Image.open(f"{gt_prefix[version]}{ground_truth_path}{true}"))

    #calculate UQI scores
    UQI_names = ['Entity']
    uqi_scores = ['UQI Scores']

    for i in range(len(ground_truth)):
        img_s = simple[i]
        img_m = medium[i]
        img_c = complex[i]
        control = truth[i]
        
        UQI_names.append(f'Complex {images_simple[i][:-4]}')
        UQI_names.append(f'Medium {images_simple[i][:-4]}')
        UQI_names.append(f'Simple {images_simple[i][:-4]}')
        
        UQI_simple = get_uqi_score(control, img_s)
        UQI_medium = get_uqi_score(control, img_m)
        UQI_complex = get_uqi_score(control, img_c)
        
        uqi_scores.append(UQI_simple)
        uqi_scores.append(UQI_medium)
        uqi_scores.append(UQI_complex)
    
    np.savetxt(f'{image_prefix[version]}UQI_scores_test.csv', [p for p in zip(UQI_names, uqi_scores)], delimiter=';', fmt='%s')
    print("Saved UQI-Score.")