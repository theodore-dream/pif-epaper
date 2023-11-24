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
def poem_step_1(creative_prompt, persona, entropy):
    # Define the function specification
    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_haiku",
                "description": "Generate a haiku poem based on the provided creative prompt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "creative_prompt": {
                            "type": "string",
                            "description": "The creative prompt to inspire the haiku"
                        }
                    },
                    "required": ["creative_prompt"]
                },
                "output": {
                    "type": "object",
                    "properties": {
                        "haiku": {
                            "type": "string",
                            "description": "The generated haiku poem"
                        }
                    }
                }
            }
        }
    ]


    # Construct the messages to be sent to the API
    messages = [
        {"role": "system", "content": persona + " Use the words in 'creative_prompt' as a base to create a new haiku poem that is three sentences of text."},
        #{"role": "user", "content": "json"},
        {"role": "user", "content": "Output json text of a haiku inspired by these words" + creative_prompt + "')"},
    ]


    # Make the API request
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        response_format={"type": "json_object"},
        messages=messages,
        seed=11111,
        temperature=0.7,
        max_tokens=500,
        tools=tools  # Include the tools parameter in the request
    )

    # Process the API response

    logger.info(f"API Response: {response}")

    try:
        if response['choices'][0]['message']['role'] == "assistant":
            # Check if tool_calls is in the response
            if "tool_calls" in response['choices'][0]['message']:
                tool_calls = response['choices'][0]['message']['tool_calls']
                if tool_calls and len(tool_calls) > 0:
                    # Assuming the first tool call contains the haiku
                    haiku_arguments = json.loads(tool_calls[0]['function']['arguments'])
                    haiku = haiku_arguments['creative_prompt']
                else:
                    haiku = "No haiku generated."
            else:
                haiku = "No tool calls in response."
        else:
            haiku = "System error occurred."
    except Exception as e:
        logger.error(f"Error processing response: {e}")
        haiku = "Error in processing response."

    return haiku


def api_poem_pipeline(creative_prompt, persona, entropy, abstract_concept):
    logger.debug(f"creative_prompt: {creative_prompt}")
    step_1_poem = poem_step_1(creative_prompt, persona, entropy)
    logger.info (f"step_1_poem:\n{step_1_poem}")
    #step_2_poem = poem_step_2(persona, entropy, step_1_poem, abstract_concept)
    #logger.info (f"step_2_poem:\n{step_2_poem}")
    #step_3_poem = poem_step_3(persona, entropy, step_2_poem)
    #logger.info (f"step_3_poem:\n{step_3_poem}")
    return step_1_poem

def parse_response(entropy):
    # this part of the code goes WAY too slow. Removing the use of nltk for initial generation of the creative_prompt words
    #creative_prompt = create_vars.gen_creative_prompt(create_vars.gen_random_words(entropy), entropy)
    creative_prompt = create_vars.gen_creative_prompt_api(entropy)
    abstract_concept = create_vars.get_abstract_concept()
    persona = create_vars.build_persona()
    lang_device = create_vars.get_lang_device()

    logger.debug(f"persona is: {persona}")
    logger.debug(f"lang_device is: {lang_device}")
    logger.debug(f"abstract_concept is: {abstract_concept}")
    logger.debug(f"entropy is: {entropy}")

    logger.debug(f"==========================")
    logger.debug(f"creative_starting_prompt: {creative_prompt}")

    poem_result = api_poem_pipeline(creative_prompt, persona, entropy, abstract_concept)
    logger.debug(f"poem result:\n{poem_result}")

    print("-" * 30)
    logger.debug("poem_gen completed successfully")
    return poem_result

#if __name__ == "__main__":
#    parse_response()


    # add tokens cost logging
    # remove the explanation for the poems its too much, useless tokens spend 
    # add proper retry logic again... I guess. Just add it to the whole thing. 

    # current issue is that there are 6 steps, 7 including the persona, and its too much complexity for the api to handle all of it
    # on the other hand the results are really good it seesm to only be going to step 3, maybe at this point I need to focus on
    # either I just want to output the final poem directly from the api but that could get dicey at different temperatures
    # alternatively I could use logic to modify the output from the api to get the final poem only. Will need to experiment on diff temps. 

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
        
