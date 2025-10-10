All of this data was generated during a master thesis titled "Illustrating GenAI knowledge bases with GenAI vision models".

This repository is organized as follows:

- Folders of generated images and prompts for the datasets "Large Scale", "Regular", and "Random". "Regular" and "Random" also include the ground-truth images used in the thesis. The dataset names mean:
    · Bias Check: A set of 500 subjects, randomly chosen from the Large Scale dataset after identifying a central person with a visible face in them, used for checking for generation biases. The traits.txt holds the traits guessed for them by Llama-4.
    · Regular: A set of 120 hand-picked subjects from GPTKB, made to fit into the categories persons, cities, landmarks, companies, products, and book-series.
    · Random: A set of 120 randomly chosen subjects from GPTKB.
    · Large Scale: The first 104,611 subjects of GPTKB v1.5.1.

- Dataset referenced in the code files, but not provided here:
    · New Random: A set of 200 randomly chosen subjects from GPTKB, different from Random.

- "python_scripts" holds all important scripts used in the thesis
    · bias_check.py: A script to make Llama-4 guess the traits ethnicity, age, and gender of the central person in each of a given list of images and save the guessed traits in a TXT file.
    · gen_image_SCADS.py: A script to generate images through the SCADS.AI-hosted stable diffusion model via an API key and save them into a folder. It includes 3 types of prompts referred to as "simple", "medium", and "complex", but they can be commented out as needed. "complex" was the type used to generate the large-scale data.
    · guessing_game.py: A script to perform the guessing game (guessing a subject from an option of 4 from a given b64 image) on a given set of images and their subjects, both without and with categories of subjects to make it harder.
    · guessing_game_tuples.py: A script to perform the tuple-based guessing game (guessing a subject from an option of 4 from a given set of tuples of its GPTKB-entry) on a given set of subjects.
    · scores_CLIP.py: A script to generate a csv-file of CLIPScores from a set of image and ground_truth-image pairs.
    · scores_UQI.py: A script to generate a csv-file of UQI scores from a set of image and ground_truth-image pairs.