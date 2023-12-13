import time
import random
from decimal import Decimal
from time import sleep

import os
import openai
#import nltk
from modules import create_vars
#from nltk.probability import FreqDist
import json
from json import loads 
from tenacity import retry, wait_random_exponential, stop_after_attempt
from typing import Dict, Optional


#from modules import logger
from modules.logger import setup_logger

#start logger
logger = setup_logger("poem_gen")
logger.debug("Logger is set up and running.")

# removed nltk to try to speed things up
#nltk.download('wordnet')
#from nltk.corpus import wordnet as wn

openai.api_key = os.getenv("OPENAI_API_KEY")

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def poem_step_1(creative_prompt, player_persona, entropy):
    CONTENT_TYPES = ["haiku", "poem", "free verse"]  # Add more poetry types as needed
    selected_content_type = random.choice(CONTENT_TYPES)
    # Inject the selected poetry type into the user message
    messages = [
        {"role": "system", "content": f"{player_persona} You output text in JSON format. You create a {selected_content_type} in a specific format. The {selected_content_type} will not exceed 3 lines. The {selected_content_type} should be in a JSON object with a single key 'Content'. For example: {{'Content': 'Roses are red.'}}."},
        {"role": "user", "content": f"Produce a {selected_content_type} inspired by {creative_prompt}. Output into JSON format as specified."},
    ]
    completion = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=(entropy),
        response_format={"type": "json_object"},
        max_tokens=500,
    )


    if completion['choices'][0]['message']['role'] == "assistant":
        step_1_response = completion['choices'][0]['message']['content'].strip()
        step_1_poem_data = loads(step_1_response)  # Parse the JSON content

        if "Content" in step_1_poem_data:
            step_1_poem = step_1_poem_data["Content"]  # Extract the poem from the parsed data
        else:
            logger.error("Content key not found in response")
            step_1_poem = "Content not generated"
    else:
        pass

    # Log the API request to keep the record of which content type was generated 
    #logger.info(f"API request step1 is message: {messages}")
    # Log the entire response for debugging
    logger.debug(f"API completion response: {completion}")
    return step_1_poem

# another API call to try to constrain the output
def poem_step_2(persona, entropy, step_1_poem, abstract_concept):

    messages = [
        {"role": "system", "content": f"{persona} You are an editor. You role is to modify the text provided to the specifications you are given. "},
        {"role": "user", "content": f"review the provided output: " + step_1_poem + " and if needed, modify the output to be less than 3 lines in a concise and artful way that retains the meaning of original content. The output should be in a JSON object with a single key 'Content'."},
    ]
    completion = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=(entropy),
        response_format={"type": "json_object"},
        max_tokens=500,
    )

    if completion['choices'][0]['message']['role'] == "assistant":
        step_2_response = completion['choices'][0]['message']['content'].strip()
        step_2_poem_data = loads(step_2_response)  # Parse the JSON content

        if "Content" in step_2_poem_data:
            step_2_poem = step_2_poem_data["Content"]  # Extract the poem from the parsed data
        else:
            logger.error("Content key not found in response")
            step_2_poem = "Content not generated"
    else:
        pass

    # Log the API request to keep the record of which content type was generated 
    #logger.info(f"API request step2 is message: {messages}")
    # Log the entire response for debugging
    logger.debug(f"API completion response: {completion}")
    return step_2_poem

def api_poem_pipeline(creative_prompt, player_persona, entropy, abstract_concept):
    logger.debug(f"creative_prompt: {creative_prompt}")
    step_1_poem = poem_step_1(creative_prompt, player_persona, entropy)
    #logger.info (f"step_1_poem:\n{step_1_poem}")
    #step_2_poem = poem_step_2(player_persona, entropy, step_1_poem, abstract_concept)
    #logger.info (f"step_2_poem:\n{step_2_poem}")
    #step_3_poem = poem_step_3(persona, entropy, step_2_poem)
    #logger.info (f"step_3_poem:\n{step_3_poem}")
    return step_1_poem

def parse_response(entropy, player_persona):
    # this part of the code goes WAY too slow. Removing the use of nltk for initial generation of the creative_prompt words
    #creative_prompt = create_vars.gen_creative_prompt(create_vars.gen_random_words(entropy), entropy)
    creative_prompt = create_vars.gen_creative_prompt_api(entropy)
    abstract_concept = create_vars.get_abstract_concept()
    lang_device = create_vars.get_lang_device()

    logger.debug(f"player_persona is: {player_persona}")
    logger.debug(f"lang_device is: {lang_device}")
    logger.debug(f"abstract_concept is: {abstract_concept}")
    logger.debug(f"entropy is: {entropy}")

    logger.debug(f"==========================")
    logger.debug(f"creative_starting_prompt: {creative_prompt}")

    poem_result = api_poem_pipeline(creative_prompt, player_persona, entropy, abstract_concept)
    logger.info(f"poem result:\n{poem_result}")

    print("-" * 30)
    logger.debug("poem_gen completed successfully")
    return poem_result

#if __name__ == "__main__":
#    parse_response()


    # add tokens cost logging
    # remove the explanation for the poems its too much, useless tokens spend 
    # add proper retry logic again... I guess. Just add it to the whole thing. 

    ## variables overview - goals
    ## build_persona - bad, needs more work / further testing, only seems to perhaps be effective with very few steps, 1-2 steps tops 
    ## get_random_words - happy with number of words because I modifed the api call to generate shorter sentence 
    ## get_abstract_concept - good, using a list and nltk to find synonyms
    ## delayed - poetic_goal ? - experimenting with this, seems like its stopping at step 3 and its step 4 now
    ## delayed - get_lang_device - seems good but needs more testing, might need to push this off for now, might be unnecesary, too much logic in a single prompt 
    ## delayed - ?incorporate the lyrics api into the poetry generator? prob save for a stage 2 

    ## other assorted ideas
    ## ====================
    ## seed the database with a script that pulls from nltk and compiles lists of words
    ## could use nltk to find synonyms for the words in the abstract concept list to seed that to the DB
    ## could find a list of meme related words somewhere, create categories, tags, individual columns or tables, etc.

    ## Parking lot - not used
        #4: {"role": "user", "content": "Step 4: Create a new poem that is two to four lines long with the following parameters: Revise the selected poem to achieve a poetic goal of expressing vivid imagery or evoking a specific emotion."},
        #5: {"role": "user", "content": "Step 5: Create a new poem that is two to four lines long with the following parameters: Consider how you could use this linguistic device: "  + lang_device + ". Revise the poem to incorporate the linguistic device"},
        
