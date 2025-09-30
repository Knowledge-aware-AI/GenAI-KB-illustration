import openai
from openai import OpenAI
import os
import time
import base64
import re
import sqlite3

# Set start time to get runtime of program later
all_start_time = time.time()

# Set the file path as a constant
gptkb_path = "GPTKB/gptkb_v1.5.1.db"  # Path to GPTKB sqlite-database

# Connect to SQLite database
connect_sql = sqlite3.connect(gptkb_path)
# Create a cursor object
cur = connect_sql.cursor()

def extract_entry(subject_uri):
    full_entry = []
    for row in cur.execute("SELECT subject, predicate, object FROM gptkb WHERE subject = ?", (subject_uri.replace("_"," "),)):
        full_entry.append(row)
    
    formatted_rows = [f"{subj} {pred} {obj}" for subj, pred, obj in full_entry]
    entry = "\n".join(formatted_rows)
    
    return entry

def get_subject(counter:int):
    query = cur.execute("SELECT DISTINCT subject FROM gptkb ORDER BY rowid LIMIT 1 OFFSET ?", (counter,)).fetchone()
    subject = query[0]
    
    return subject

def generate_image_with_retry(prompt, subject, vision_model, size="1024x1024"):
    attempt = 0
    responded = False
    while not responded:
        try:         
            response = client_tu.images.generate(
                model=vision_model,
                prompt=prompt,
                n=1,
                size=size,
                response_format="b64_json"
            )
            
            attempt = attempt + 1
            if attempt > 1:
                print(f"Generated image on {attempt}. try.")
            
            return response.data[0].b64_json, prompt
        except openai.RateLimitError:
            wait_time = min(2 ** attempt, 60)
            print(f"Rate limit hit. Retrying in {wait_time} seconds...")
            attempt = attempt + 1
            time.sleep(wait_time)
        except openai.BadRequestError as er:
            #print(f"Error: {er}")
            print(f"Problematic Prompt: {prompt}\n"
                  f"Retrying with new Prompt."
                )
            attempt = attempt + 1
            prompt = generate_prompt(subject, extract_entry(subject), prompt, "bad prompt")
        except (openai.InternalServerError, openai.AuthenticationError) as e:
            print(f"{e}")
            print("Can't reach server, trying again in 10 minutes.")
            time.sleep(600)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    return None

def generate_prompt(current_subject, current_entry, prompt, prompt_type:str, retries=5):
    for attempt in range(retries):
        try:
            match prompt_type:
                case "simple":
                    # simple prompt
                    content = f"Make this correct: An image of {current_subject}. Make sure to respond with only the corrected word group and nothing more. You are only allowed to add a or an if necessary."
                case "medium":
                    # medium prompt
                    content = f"You are an AI artist. Create a prompt to generate a representative image for this: {current_subject}. Do not be too wordy. Keep the prompt to 3-5 sentences. Respond with only the prompt and nothing more."
                case "complex":
                    # complex prompt
                    content = (
                        f"You are an AI artist and are supposed to create a prompt for image generation."
                        f"You are to create a prompt for a representative image of this: {current_subject}."
                        f"The \"gptkbp:instance_of\" property usually states the type of the subject."
                        f"Make sure to get the right type since some subjects might have ambiguous names."
                        f"Entry: {current_entry}"
                        f"If the entry has a \"population\" property, you cannot under any circumstances use a person type. Look for a non-person alternative with the same name."
                        f"The style should make sense for the subject depicted. Real subjects like cities or people should be depicted realistically."
                        f"Respond with only the prompt and nothing more."
                    )
                # regenerating a prompt if no image could be created for it because of the wording
                case "bad prompt":
                    content = (
                        f"You created this prompt to generate an image via DALL-E 2, but it causes an error: {prompt}"
                        f"Replace any part of the prompt that might cause problems."
                        f"If there is the name of a person in the prompt, remove it."
                        f"Remove words with R-rated conotations and uses."
                        f"Replace all possible words with synonyms."
                        f"Paraphrase words and phrases that could be misunderstood or have explicit conotations."
                        f"Never write monkey or ape or any synonym for them, always describe them instead."
                        f"Keep the prompt PG-13."
                        f"Only change the number of sentences if really necessary and only by a maximum of 2 senteces more or less."
                        f"Respond with only the prompt and nothing more."
                    )
                case _:
                    print("No prompt type was specified!")
                    break  
            response = client_tu.chat.completions.create(
                messages=[{"role":"user","content":content}],
                model=model_name
                )
            
            return response.choices[0].message.content
        except openai.RateLimitError:
            wait_time = min(2 ** attempt, 60)
            print(f"Rate limit hit. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        except openai.BadRequestError as er:
            print(f"Error: {er}")
            current_entry = "\n".join(current_entry.splitlines()[:-1])
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    return None

def safe_filename(name: str) -> str:
    # Replace all invalid filename characters with underscore
    clean = re.sub(r'[\\/*?:"<>|]', "_", name)
    # Strip leading/trailing spaces and dots
    clean = clean.strip(" .")
    
    return clean

folder_paths = ["large_scale"]
used_variant = ["Large Scale"]

# generate prompts
# Set SCADS.AI API key
client_tu = OpenAI(
    base_url = "https://llm.scads.ai/v1",
    api_key = os.environ.get("TU_API_KEY")
)

# Find model with "llama" in name
for model in client_tu.models.list().data:
    #print(model.id)  # using meta-llama/Llama-4-Scout-17B-16E-Instruct; if it is not responsive Llama-3-Scout can be used with a smaller context window
    model_name = model.id
    if "Llama-4" in model_name:
        break

# Find model with "stable-diffusion" in name
for model in client_tu.models.list().data:
    #print(model.id)  # using meta-llama/Llama-4-Scout-17B-16E-Instruct
    vision_model = model.id
    if "stable-diffusion" in vision_model:
        break

subject_check = {}
variant = 0
run_time_start = time.time()
i = 0      # starting offset in the database for generation process, should be 0 to start at beginning

gen_images = os.listdir(r"large_scale/")  # folder into which the images will be saved, needed to check for duplicates
generated_images = len(gen_images)

while generated_images <= 100000:   # limit for how many images should be created
    generated = False
    start_time = time.time()
    
    # get subject
    subject = get_subject(i)
    clean_subject = safe_filename(subject)
    
    while os.path.isfile(f'{folder_paths[variant]}/gen_images/{clean_subject}.png'):
        if subject == subject_check.get(clean_subject):
            print(f"Already generated {clean_subject}.png")
            generated = True
            break
        elif clean_subject not in subject_check:
            subject_check.update({clean_subject:subject})
        else:
            clean_subject = clean_subject + "_1"
            print(f"{subject} shared clean_subject with another subject. It has been renamed to {clean_subject} to avoid confusion.")
    
    # continue to next subject if it was actually generated before
    if generated:
        i = i + 1
        continue
    
    # update subject:clean_subject dictionary
    subject_check.update({clean_subject:subject})
    
    ############ This commented out part can be used to check the extraction speed but is not functionally necessary ########
    # extract entries
    #entry.update({clean_subject:extract_entry(f"{subject}")})
    
    #print("Entry extraction: --- %s seconds ---" % (time.time() - start_time))
    #start_time = time.time()
    
    
    # create prompts
    # Use model for simple
    response_simple = generate_prompt(clean_subject, extract_entry(subject), None, "simple")
    
    # Use model for medium
    response_medium = generate_prompt(clean_subject, extract_entry(subject), None, "medium")

    # Use model for complex
    response_complex = generate_prompt(clean_subject, extract_entry(subject), None, "complex")
    #print(extract_entry(subject))
    print("Entry extraction and prompt generation: --- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    
    # simple
    # Extract image URL and save prompts that were actually used to generate an image
    image_b64, simple_prompt = generate_image_with_retry(response_simple, clean_subject, vision_model)
    if image_b64:
        # Download the image
        image_response = base64.b64decode(image_b64)
        # Save the image
        if image_response != None:
            with open(f'{folder_paths[variant]}/gen_images_simple/{clean_subject}_simple.png', 'wb') as f:
                f.write(image_response)
            with open(f'{folder_paths[variant]}/gen_images/{clean_subject}_simple.png', 'wb') as f:
                f.write(image_response)
            print(f"Image downloaded and saved as {clean_subject}_simple.png")
        else:
            print("Failed to download the image")
     
    with open(f'{folder_paths[variant]}/prompts/{clean_subject}_simple.txt', 'w', encoding="utf-8") as s_prompt:
        print(simple_prompt, file=s_prompt)
    
    print("Gen simple: --- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    
    # medium
    # Extract image URL
    image_b64, medium_prompt = generate_image_with_retry(response_medium, clean_subject, vision_model)
    if image_b64:
        # Download the image
        image_response = base64.b64decode(image_b64)
        # Save the image
        if image_response != None:
            with open(f'{folder_paths[variant]}/gen_images_medium/{clean_subject}_medium.png', 'wb') as f:
                f.write(image_response)
            with open(f'{folder_paths[variant]}/gen_images/{clean_subject}_medium.png', 'wb') as f:
                f.write(image_response)
            print(f"Image downloaded and saved as {clean_subject}_medium.png")
        else:
            print("Failed to download the image")
     
    with open(f'{folder_paths[variant]}/prompts/{clean_subject}_medium.txt', 'w', encoding="utf-8") as s_prompt:
        print(medium_prompt, file=s_prompt)
    
    print("Gen medium: --- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    
    # complex  
    # Extract image URL
    image_b64, complex_prompt = generate_image_with_retry(response_complex, clean_subject, vision_model)
    if image_b64:
        # Download the image
        image_response = base64.b64decode(image_b64)
        # Save the image
        if image_response != None:
            #with open(f'{folder_paths[variant]}/gen_images_complex/{clean_subject}_complex.png', 'wb') as f:
            #    f.write(image_response)
            with open(f'{folder_paths[variant]}/gen_images/{clean_subject}.png', 'wb') as f:
                f.write(image_response)
            print(f"Image downloaded and saved as {clean_subject}.png")
        else:
            print("Failed to download the image")
    
    with open(f'{folder_paths[variant]}/prompts/{clean_subject}.txt', 'w', encoding="utf-8") as s_prompt:
        print(complex_prompt, file=s_prompt)
    
    print("Generation: --- %s seconds ---" % (time.time() - start_time))
    
    i = i + 1
    
    if ((i+1) % 2000) == 0:
        print("All: --- %s seconds ---" % (time.time() - all_start_time))
    
    generated_images = generated_images + 1
    
    # short delay between image sets
    time.sleep(1.5)

#print("All: --- %s seconds ---" % (time.time() - all_start_time))      # uncomment if complete runtime should be printed into log