import os
import openai
from openai import OpenAI
import time
import base64

def guess_traits(base64_image, retries=3):
    instructions = (
        "Look at the given image and guess certain traits of the central person in the image."
        "Your answer should have this format:"
        "[Ethnicity];[Age];[Gender]"
        "Ethnicity and Gender have to be a single word each."
        "Be sure not to use potentially racist words for Ethnicity."
        "Age has to be a single integer."
        "Do not write the [] and only return the filled in traits as shown before."
        "Make sure you give all answers for the image given!"
    )

    for attempt in range(retries):
        try:
            response = client_tu.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": instructions},
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
        except (openai.InternalServerError, openai.AuthenticationError) as e:
            print(f"{e}")
            print("Can't reach server, trying again in 10 minutes.")
            time.sleep(600)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    return None

#set scads.ai API key
my_api_key = os.environ.get("TU_API_KEY")
client_tu = OpenAI(base_url="https://llm.scads.ai/v1",api_key=my_api_key)

# Find model with "llama" in name
for model in client_tu.models.list().data:
    #print(model.id)  
    model_name = model.id
    if "Llama4" in model_name:
        break

image_path = r"large_scale/bias_check"
all_images = os.listdir(image_path)
text = ["Subject;Ethnicity;Age;Gender"]

for image in all_images:    
    with open(f"{image_path}/{image}", "rb") as image_file:
        b64image = base64.b64encode(image_file.read())
        
    answer = guess_traits(b64image)
    
    subject = image.removesuffix(".png")
    
    print(f"Guessed traits for {subject}.")
    text.append(f"{subject};{answer}")
        
    time.sleep(0.5)

# Save to file
with open("large_scale/traits.txt", "w", encoding="utf-8") as txt_file:
    for subj in text:
        txt_file.write(subj + "\n")

print(f"Saved TXT-file as \"traits.txt\".")