import random
import os
import openai
from openai import OpenAI
import time
import base64
import pandas as pd

def guessing_game(base64_image, retries=3):
    game_rules = (
        "Let's play a guessing game! "
        "Look at the image and guess which of these 4 subjects it is. "
        f"These are the possible subjects: {guess_options}. "
        "Respond with only the subject you guessed and nothing more."
    )

    for attempt in range(retries):
        try:
            response = client_tu.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": game_rules},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image.decode('utf-8')}"
                                },
                            },
                        ],
                    }
                ],
            )
            return response.choices[0].message.content
        except openai.RateLimitError:
            wait_time = min(2 ** attempt, 60)
            print(f"Rate limit hit. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        except openai.InternalServerError:
            print("Server didn't respond. Retrying.")
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

def get_guess_options1(true_subject:str):   
    random_subjects = ""
    
    same_category = find_origin_list(true_subject)
    
    while random_subjects == "":
        randomized = random.sample(same_category,k=3)
        if true_subject not in randomized:
            random_subjects = ",".join(randomized)
    
    rndm_subjects = f"{true_subject},{random_subjects}"
    
    options = rndm_subjects.split(",")
    copy_options = options.copy()
    while options==copy_options:
        random.shuffle(options)
    
    return options

def find_origin_list(true_subject):
    same_category = []
    
    cat_list = categories[variant].copy()
    
    for category in range(len(cat_list)):
        if true_subject in cat_list[category]:
            same_category = cat_list[category].copy()
            return same_category

def parse_file_name(file_name):
    if '_' not in file_name:
        return None, None
    subject, difficulty = file_name.rsplit('_', 1)
    return subject

#set scads.ai API key
my_api_key = os.environ.get("TU_API_KEY")
client_tu = OpenAI(base_url="https://llm.scads.ai/v1",api_key=my_api_key)

# Find model with "llama" in name
for model in client_tu.models.list().data:
    #print(model.id)  
    model_name = model.id
    if "Qwen2" in model_name:
        break

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

# Path to the saved txt file
file_path = "sampled_subjects.txt"

# Load subjects into a list, replacing spaces with underscores
with open(file_path, "r", encoding="utf-8") as f:
    rndm_sbjcts = [line.strip().replace(" ", "_").replace(":", "") for line in f if line.strip()]

# Path to the saved txt file
file_path1 = "new/sampled_subjects.txt"

# Load subjects into a list, replacing spaces with underscores
with open(file_path1, "r", encoding="utf-8") as f:
    rndm_sbjcts1 = [line.strip().replace(" ", "_").replace(":", "") for line in f if line.strip()]

##### FOR SCLAE TEST SUBJECTS
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

subjects = [rnd3_subjects,rnd3_subjects]
image_path = [r"scale_test/gen_images/",r"scale_test/gen_images/"]
gen_variant = ["Scale Test Random","Scale Test Random Reuse"]

for i in range(6):
    for variant in range(len(subjects)):
        text = []
        files = os.listdir(image_path[variant])

        for count,_ in enumerate(subjects[variant]):
            #subject = parse_file_name(file)
            
            if variant == 0:
                subject = rnd3_subjects[count]
            else:
                subject = rnd3_sim_subj[count]
            
            guess_options = get_guess_options(subject, subjects[variant])
            
            with open(f"{image_path[variant]}/{subject}.png", "rb") as image_file:
                b64image = base64.b64encode(image_file.read())
            
            guess = guessing_game(b64image)
            print(f"Guess made for {subject}.")
            
            text.append(f"{subject}: {guess_options} --- {guess}")
            time.sleep(1)
        
        save_path = image_path[variant].replace("gen_images/","")
        
        # Save to file
        with open(f"{save_path}guessing_game_lv0_{gen_variant[variant]}_0{i}.txt", "w", encoding="utf-8") as txt_file:
            for subj in text:
                txt_file.write(subj + "\n")
        
        print(f"Saved TXT-file as \"{save_path}guessing_game_lv0_{gen_variant[variant]}_0{i}.txt\".")

############################# LEVEL 1 #################################

chosen_categories = [
    chosen_subjects[0:20],    # Category 0
    chosen_subjects[20:40],   # Category 1
    chosen_subjects[40:60],   # Category 2
    chosen_subjects[60:80],   # Category 3
    chosen_subjects[80:100],  # Category 4
    chosen_subjects[100:120],  # Category 5
]

random_categories = [
    [  # historical_figures_military_leaders
        "Filippo_Strozzi_the_Younger",
        "Bernhard_of_Carinthia",
        "Brigadier_General_Janis_Sprogis",
        "Radomir_Putnik",
        "Henry_Fairfax,_2nd_Lord_Fairfax_of_Cameron",
        "General_Nguyen_Van_Hinh",
        "Guillaume,_Count_of_Flanders",
        "George_Burnham_Jr.",
        "Joseph_Sewall_III",
        "Michele_A._Lee",
        "Mary_Fitz_Roy,_4th_Duchess_of_Richmond",
        "Boris_Hybner"
    ],
    [  # wars_battles_military_events
        "Second_Anglo-Boer_War",
        "Battle_of_Håkonarstadir",
        "Capture_of_Fukuoka_Castle",
        "Battle_of_Yavin",
        "29th_Logistics_Support_Battalion",
        "U._N._forces",
        "Karpov_vs_Korchnoi,_Game_19",
        "The_Battle_of_the_Shining_Walls",
        "Congo_Free_State_Administration",
        "UN_Security_Council_Resolution_1704",
        "German_Freikorps",
        "1958_Baghdad_Pact_withdrawal"
    ],
    [  # arts_music_performance
        "Agnès_Baltsa",
        "Ms._Pat",
        "Un_Verano_Sin_Ti_(Deluxe)",
        "Symphonic_Live",
        "Sérgio_Reis_-Ao_Vivo_(2015)",
        "LCD_Soundsystem_-This_Is_Happening",
        "The_Style_Council_Big_Band",
        "Flair_for_Fashion",
        "Perlman_Plays_Tchaikovsky",
        "The_New_England_Transcendentalists",
        "Giorgio_Graziani",
        "Detective_Philippe_Rousselot"
    ],
    [  # literature_philosophy_publishing
        "Prabhat_Prakashan",
        "Dr._Richard_N._Longenecker",
        "Algari_Rose",
        "The_Binti_Universe",
        "Bloomsbury_Publishing_Grenada",
        "Sri_Bhashya",
        "Murakami_vs._Murakami_(2016)",
        "Richard_Day",
        "George_M._Marakas",
        "The_Merchant_of_Venice_(Broadway)",
        "The_Immortal_Hulk_Vol._10",
        "Lemaître's_redshift",
        "Marta_Lobo_Antunes"
    ],
    [  # cities_regions_places
        "Ceres,_California",
        "Tlaquepaque",
        "Malden_City_Hall",
        "Pingtung_County_Government",
        "Riga's_Historic_Centre",
        "Zalaegerszeg_Adventure_Park",
        "Kintai_Bridge_Park",
        "Bahawalpur_Technical_Institute",
        "Churfirsten",
        "Sheffield_to_Brora_Line",
        "Cott_Canada",
        "St._Albans_City_School_District",
        "Principality_of_Antioch",
        "Erfurt_Hauptbahnhof"
    ],
    [  # government_law_politics
        "Governor_of_Colorado_Territory",
        "Cherokee_Nation_v._United_States_Department_of_the_Navy",
        "567_U._S._709",
        "Ajman_Free_Zone_Authority",
        "Liberty_Global_Partnerships",
        "Massachusetts_Route_9_G",
        "Ascanian_coat_of_arms",
        "Ammonius_Hermiae",
        "Palazzo_Ca'_Corner_della_Regina",
        "Seguin_Transit",
        "Baron_of_the_Isle_of_Benbecula"
    ],
    [  # media_film_television
        "Dennis_the_Menace_Strikes_Again",
        "And_Then_We_Danced",
        "NBC_Sports_Washington's_The_Game_Plan",
        "Best_Music_at_the_BAFTA_Games_Awards_2016",
        "Screamfest_Horror_Film_Festival_2008",
        "Captain_America_#42",
        "K9999",
        "Gisele_Yashar",
        "Wizarding_Wireless_Network",
        "Vikram_Aur_Betaal",
        "Cagayake!_GIRLS",
        "Bell_Productions",
        "Paramount_D._Smith"
    ],
    [  # museums_parks_culture_sites
        "The_Museum_of_Contemporary_Art_in_Bakersfield",
        "Matsuyama_City_Museum_of_Poetry",
        "Busan_Sajik_Stadium",
        "Ban_Chiang_archaeological_site",
        "the_Benin_ceremonial_drum",
        "fresco_of_the_Sacred_Snake",
        "Tokyo_Metropolitan_University_Athletic_Association",
        "Molly_Meldrum_Foundation",
        "Molesworth_Airfield",
        "Valkenburg_railway_station",
        "Hiroshima_University_School_of_Dentistry",
        "Great_River_Station",
        "Yokohama_Hakkeijima_Sea_Paradise"
    ],
    [  # sports_games_competitions
        "Rally_of_Czech_Republic",
        "All_Blacks_Sevens",
        "Chico_the_Jet_Hawk",
        "Puzzle_Bobble_Infinity",
        "Rurouni_Kenshin_Kengeki_Kenran_26",
        "Brit_Asia_TV_Music_Awards",
        "KSL_City_Mall",
        "Lizarazu",
        "Vladimir_Stimac",
        "Dodge_Dart_Rallye",
        "Eddie_Goldman"
    ],
    [  # science_tech_industry
        "Ge_Force_GPU",
        "Stila",
        "Paligo",
        "FENSTERBAU_FRONTALE",
        "Piano_Sonata_No._19_in_C_major,_Op._2",
        "the_presidential_seal_of_Mexico",
        "H._C._Mc_Culloch",
        "Kordes'_'_Sunsprite'_rose",
        "Thomas_Saltonstall"
    ]
]

random_categories1 = [
    [  # historical_figures_political_military
        "Jean_Kinkaid",
        "Sir_Syed_Aftab_Ahmad",
        "Madho_Singh",
        "Neil_Dunn",
        "Bishop_Emeritus_S%C3%A9amus_Hegarty",
        "Starost_of_Samogitia",
        "Winifred_Frances_Knox",
        "Pauline_Roccucci",
        "Charles_W._Harkness",
        "Pius_Langa",
        "Anna_Amalia%2C_Countess_of_Nassau-Siegen",
        "Pamela_Hill",
        "Wong_Ting-kwong",
        "Grant_Sawyer",
        "Richard_Jones%2C_1st_Earl_of_Ranelagh",
        "Frances_Contreras",
        "Jennifer_Jordan",
        "Deputy_Inspector_Genevieve_Isom",
        "Giovanni_Migliara",
        "Florence_Laing_Kennedy",
        "Serhiy_Honcharenko",
        "Emperador_de_toda_Espa%C3%B1a",
        "Admiral_Am%C3%A9d%C3%A9e_Courbet"
    ],
    [  # geography_places_infrastructure
        "Medway_Valley_Walk",
        "Maracas_Waterfall",
        "Dean_Prior",
        "Bad_Kreuzen",
        "Bogorodsk",
        "Durbar_Square",
        "Launceston%2C_Cornwall%2C_England",
        "Keller%2C_Indiana",
        "June_Park",
        "Seattle%2C_Washington%2C_USA",
        "Dinefwr_Borough_Council",
        "Chevry",
        "Solna_Municipality%2C_Sweden",
        "Great_Abaco_Island",
        "Diamond_Hill_MTR_Station",
        "SE_Flavel_Street",
        "River_Kensey",
        "Naoshima",
        "McLain%2C_Mississippi%2C_USA",
        "Northern_California%2C_United_States",
        "Ume%C3%A5%E2%80%93%C3%96stersund",
        "Lotnisko_Chopina_w_Warszawie",
        "Spruceton_Trail",
        "Astley_Castle",
        "Calaboose_African_American_History_Museum",
        "Iosan",
        "Lotnisko_Chopina_warszawie",
        "Augusta,_Georgia",
        "Jamestown,_Virginia",
        "Zaandam",
        "Nordvestpassagen._Gj%C3%B8a-ekspeditionen_1903%E2%80%931907",
        "Chinbrook_Community_Centre",
        "Bursa_Cable_Car",
        "Noor_Bank_Metro_Station",
        "NY_9A",
        "Chekhov%2C_Russia"
    ],
    [  # technology_computing_transport
        "HAL_Laboratory",
        "Tridium",
        "llvm-readobj",
        "Honeywell_MAXPRO",
        "Environmental_testing_%E2%80%93_Part_1%3A_General_and_guidance",
        "Backdoor.Winstar.AH",
        "Optiver",
        "Protected_Management_Frames_%28PMF%29",
        "MF_trains",
        "Nokia_6800",
        "BMT_Broadway_Line",
        "Mumbai_Metro_Line_27",
        "Google_Developer_Experts",
        "Audiohammer_Studios",
        "ASME_B107.26-2003",
        "State_Road_75",
        "New_Hampshire_Route_286A",
        "French_National_Railways",
        "Gauss_lunar_crater",
        "Russian_Missile_Design_Bureau",
        "Oldsmobile_98_Regency_Touring_Brougham",
        "Maybach_SW_38"
    ],
    [  # arts_culture_literature
        "The_Delinquent_Season",
        "KRS-One_%E2%80%93_KRS-One",
        "Hungarian_fairy_tales",
        "The_Caves_of_Mars",
        "The_Unicorn_in_Captivity",
        "The_Citadel_of_Chaos",
        "The_Rock_of_Tanios",
        "Crostata_di_ricotta_e_visciole",
        "The_Art_of_Readable_Code",
        "A_Natural_History_of_New_York_City",
        "Fly_Your_Dreams",
        "Symphony_No._1_in_E_major%2C_Op._5",
        "All_That_You_Dream",
        "Anna_Karenina_%281935_film%29",
        "The_Dark_Tower",
        "The_Prisoner_of_the_Devil",
        "Fortitude%3A_The_D-Day_Deception_Campaign",
        "Thief_in_the_Night",
        "Fortitude_The_D-Day_Deception_Campaign",
        "The_Confessions_of_a_Holiday_Camp",
        "Frank_Butcher",
        "Hoppy_Uniatz"
    ],
    [  # education_science_language
        "College_of_Business_and_Professional_Studies",
        "Baker_Heart_and_Diabetes_Institute",
        "Hezhe_language",
        "English_College_for_Catholic_priests",
        "Lahore_College_for_Women_University",
        "FSU_Student_Legal_Services",
        "Dynamics_of_Prejudice",
        "Maryam_Nassir_Zadeh",
        "Serena_Nik-Zainal",
        "Acoma_Pueblo_people",
        "Amt_II_%28Economic_Affairs%29",
        "Lipsha_Horowitz",
        "Empetrum_nigrum",
        "white-eyed_gull",
        "Orseolia",
        "South_American_indigenous_peoples"
    ],
    [  # music_entertainment_media
        "Steinway_Artists",
        "I_Wonder_Where_My_Baby_Is_Tonight",
        "Let_Them_Eat_Flax",
        "Foster_the_People_-_Don%27t_Stop_%28Color_on_the_Walls%29",
        "Seth_Lakeman_Band",
        "Chris_Cain_%28self-titled_album%29",
        "Zula_Sound_Bar",
        "L%27ultimo_guerriero",
        "Ascenseur_pour_l%27%C3%A9chafaud_%28soundtrack%29",
        "Yu-Gi-Oh%21_Rush_Duel%3A_Saikyou_Battle_Royale%21%21",
        "Social_Outcast",
        "Tales_of_the_Sinestro_Corps",
        "Jack_Hanna%27s_Animal_Adventures",
        "Jamie_Kerstetter",
        "Cory_Rooney",
        "Zentralquartett",
        "Manta_Pack_Back_Bling",
        "Tea_Cups",
        "Third_Eye_Blind_%28album%29",
        "Vielklang_Studios",
        "Northwest_Public_Radio"
    ],
    [  # religion_myth_history_misc
        "Innsmouth_Hardware_Store",
        "Pate_Lucid",
        "Tsuru",
        "General_Who_Defeats_Bandits",
        "Sheo",
        "Adam_%28biblical_figure%29",
        "House_of_Ayala",
        "Amal_al-Jarari",
        "Amir_Mann",
        "Lord_Camber%27s_Ladies",
        "Donald_Wiseman",
        "James_Wallace_%28pirate%29",
        "Archbishop_of_Corfu",
        "Hugh_MacDonald%2C_1st_of_Sleat",
        "Aunt_Aggie",
        "Cemetery_of_the_Priests",
        "Taiwan_Creative_Content_Agency",
        "Kim_Gyeong-hwa",
        "Sisters_of_St._Francis%2C_Oldenburg",
        "Aassoun",
        "Dioecesis_Tusculana"
    ],
    [  # politics_law_government
        "Strategic_Arms_Reduction_Treaty_signed",
        "Public_Law_100-119",
        "New_York_State_of_Health",
        "Embassy_of_Poland_in_Budapest",
        "State_Reception_Center",
        "Liberal_Party_of_Russia",
        "Duke_of_Bir%C5%BEai_and_Dubingiai",
        "Dvach",
        "New_York_Herald_building",
        "Propaganda_and_Censorship_during_Canada%27s_Great_War",
        "20th_Space_Range_Squadron",
        "Ashley_Horace_Thorndike"
    ],
    [  # sports_travel_local_culture
        "Stourbridge_Line",
        "Walker_Ranch_Loop_Trail",
        "South_Lake_Lean-to",
        "Camberwell_Market",
        "1937_Donington_Grand_Prix",
        "Women%27s_Artistic_Gymnastics_All-Around",
        "Fight_of_the_Night%3A_Manel_Kape_vs._Felipe_dos_Santos",
        "FC_Cambuur",
        "Popatlal",
        "Illari",
        "Glic%C3%A9rio",
        "Hjemkomst_Center",
        "Garden_of_the_Gods_Observation_Trail",
        "Cata%C3%B1o%E2%80%93San_Juan_ferry_route",
        "Welsh_Athletics_Hall_of_Fame",
        "Lambay_Whiskey",
        "Aldo_Pedro_Poy",
        "2012_All-Star_Game"
    ],
    [  # people_other
        "Thomas_Rastrick_%28son%29",
        "Dave_Alvin",
        "Ramey_Jackson",
        "Daniel_Briley",
        "Anu_Noorma",
        "Kitchie_Benedicto",
        "Julie_Manet",
        "Geraldine_Picaud",
        "Mary_Belin_du_Pont",
        "Vicki_Kimm",
        "Jason_Brown",
        "Jane_Greenwood",
        "Enrico_Coveri",
        "Lindsey_Pfaff",
        "Francisco_del_Villar"
    ]
]

categories = [chosen_categories,random_categories,chosen_categories,random_categories,random_categories1]

#for i in range(6):
#    for variant in range(len(image_path)):
#        text = []
#        files = os.listdir(image_path[variant])
#        
#        j = 0
#                
#        for file in files:
#            subject = parse_file_name(file)
#            guess_options = get_guess_options1(subject)
#            
#            with open(f"{image_path[variant]}/{file}", "rb") as image_file:
#                b64image = base64.b64encode(image_file.read())
#            
#            guess = guessing_game(b64image)
#            print(f"Guess made for {subject}.")
#            
#            text.append(f"{subject}: {guess_options} --- {guess}")
#            
#            if j % 10 == 0:
#                time.sleep(1)
#            j = j+1
#        
#        save_path = image_path[variant].replace("gen_images/","")
#        # Save to file
#        with open(f"{save_path}guessing_game_lv1_{gen_variant[variant]}_0{i}.txt", "w", encoding="utf-8") as txt_file:
#            for subj in text:
#                txt_file.write(subj + "\n")
#        
#        print(f"Saved TXT-file as \"{save_path}guessing_game_lv1_{gen_variant[variant]}_0{i}.txt\".")
