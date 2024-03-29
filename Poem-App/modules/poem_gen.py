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
def initial_gametext_api(entropy, player_persona, creative_prompt, abstract_concept):
    APPROACH_TYPES = [
        "You might dislike the person you're talking to but you still want to talk to them",
        "You are very interested in the person you're talking to and want to win them over but are playing it cool.",
        "You have no opinion as to your relationship with the person you are speaking to and have no particular like or dislike of them"
    ]
    selected_approach = random.choice(APPROACH_TYPES)
    #logger.info(f"selected_approach_type: {selected_approach}")
    # Inject the selected poetry type into the user message
    messages = [
        {
            "role": "system",
            "content": f"This is a description of who you are. {player_persona}. "
                    "You output text in JSON format. The output should be between one and three lines." 
                    "Your output should be in a JSON object with a single key 'Content'. "
                    f"For example: {{'Content': 'Roses are red.'}}."
        },
        {
            "role": "user",
            "content": f"You speak directly and plainly." 
 #                   f"Consider incorporating {creative_prompt} in your speech if it may help you communicate."
 #                   "You are introducing yourself. This is your first interaction."
                    "I want you to remember you are having a conversation. "
                    #f"{selected_approach}"
                    "Output into JSON format as specified."
        },
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=(entropy * 2),
        response_format={"type": "json_object"},
        max_tokens=500,
    )

    if completion['choices'][0]['message']['role'] == "assistant":
        api_response = completion['choices'][0]['message']['content'].strip()
        api_poem_data = loads(api_response)  # Parse the JSON content

        if "Content" in api_poem_data:
            api_poem = api_poem_data["Content"]  # Extract the poem from the parsed data
        else:
            logger.error("Content key not found in response")
            api_poem = "Content not generated"
    else:
        pass

    # Log the API request to keep the record of which content type was generated 
    #logger.info(f"API request step1 is message: {messages}")
    # Log the entire response for debugging
    logger.debug(f"API completion response: {completion}")
    return api_poem

# another API call to try to constrain the output
# this API call is called reaction specifically because it takes in the player_gametext and reacts to it. 
def reaction_gametext_api(entropy, persona, player_gametext, creative_prompt, abstract_concept):
    REACTION_TYPES = [
        "You strongly dislike the person you're talking to and want to make it clear you no longer want to talk to them",
        "You are very interested in the person you're talking to and want to show your interest.",
        "You have no opinion as to your relationship with the person you are speaking to and have no particular like or dislike of them"
    ]
    selected_reaction_type = random.choice(REACTION_TYPES)
    #logger.info(f"selected_reaction_type: {selected_reaction_type}")
    # Inject the selected poetry type into the user message

    messages = [
        {
            "role": "system",
            "content": (
                f"This is a description of who you are. {persona}. You are a person having a conversation. You are getting to know one another."
                "You will respond to the provided speech "
                "and incorporate the provided creative prompt and abstract concepts while still maintaining a conversational tone. "
                "The output should be in a JSON object with a single key 'Content'. For example: {'Content': 'Roses are red.'}."
            )
        },
        {
            "role": "user",
            "content": (
                f"You are having a conversation. This is what they just said to you {player_gametext}. Review this provided input and " 
                f"consider your response. You may choose to be inspired by the following words: {creative_prompt}."
                f"you may want to consider incorporating {abstract_concept}. If needed, modify the output to be less than 3 lines in a concise"
                "and artful way that retains the meaning of original content. Remember you're having a conversation."
                #f"{selected_reaction_type}"
                "you have no opinion as to your relationship with the person you are speaking to and have no particular like or dislike of them."
                "The output should be in a JSON object with a single key 'Content'."
            )
        }
    ]
    
    completion = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=(entropy * 2),
        response_format={"type": "json_object"},
        max_tokens=500,
    )

    if completion['choices'][0]['message']['role'] == "assistant":
        api_response = completion['choices'][0]['message']['content'].strip()
        api_poem_data = loads(api_response)  # Parse the JSON content

        if "Content" in api_poem_data:
            match_api_output = api_poem_data["Content"]  # Extract the poem from the parsed data
        else:
            logger.error("Content key not found in response")
            match_api_output = "Content not generated"
    else:
        pass

    # Log the API request to keep the record of which content type was generated 
    #logger.info(f"API request step2 is message: {messages}")
    # Log the entire response for debugging
    logger.debug(f"API completion response: {completion}")
    return match_api_output

# this API call is called conversation specifically because it takes in the conversation and reacts to it. 
def conversation_gametext_api(entropy, persona, conversation, creative_prompt, abstract_concept):
    # Inject the selected poetry type into the user message

    messages = [
        {
            "role": "system",
            "content": (
                f"This is a description of who you are. {persona}. You are a person having a conversation. You are getting to know one another"
                "asking each other questions, and answering them. You will respond to the provided speech."
                "The output should be in a JSON object with a single key 'Content'. For example: {'Content': 'Roses are red.'}."
                "The output should be between one and three lines."
                f"You will be asked to review the history of the conversation you've been having."
                f"You will be asked to consider being inspired by a set of random words and an abstract concept. This is optional to include in your output." 
                f"This is the context of the conversation you're having:{conversation} " 
                f"consider your response. You may choose to be inspired by the following words: {creative_prompt}."
                f"You may also choose to be inspired by the following abstract concept: {abstract_concept}."
            )
        },
        {
            "role": "user",
            "content": (
                f"Say what you want to say in one to three lines. Think about who you are and what you know about the person you're talking to."
                "Do you want to know more about this person? Maybe ask them a question. Have they mentioned something maybe you could follow up on?"
                "Do you like them? Do you dislike them? Do you know? What would you need to know to determine that?"
                "It is more important that you engage your conversation partner than it is to use any of the provided input."
                "The output should be between one and three lines."
                "The output should be in a JSON object with a single key 'Content'."
            )
        }
    ]
    
    completion = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=(entropy * 2),
        response_format={"type": "json_object"},
        max_tokens=500,
    )

    if completion['choices'][0]['message']['role'] == "assistant":
        api_response = completion['choices'][0]['message']['content'].strip()
        api_poem_data = loads(api_response)  # Parse the JSON content

        if "Content" in api_poem_data:
            match_api_output = api_poem_data["Content"]  # Extract the poem from the parsed data
        else:
            logger.error("Content key not found in response")
            match_api_output = "Content not generated"
    else:
        pass

    # Log the API request to keep the record of which content type was generated 
    #logger.info(f"API request step2 is message: {messages}")
    # Log the entire response for debugging
    logger.debug(f"API completion response: {completion}")
    return match_api_output

def gen_conversation(persona_name, entropy, persona_data, conversation):
    #creative_prompt = create_vars.gen_creative_prompt(create_vars.gen_random_words(entropy), entropy)
    creative_prompt = create_vars.gen_creative_prompt_api(entropy)
    abstract_concept = create_vars.get_abstract_concept()
    lang_device = create_vars.get_lang_device()

    logger.info(f"==========================")
    logger.info(f"persona_name is: {persona_name}")
    logger.info(f"lang_device is: {lang_device}")
    logger.info(f"abstract_concept is: {abstract_concept}")
    logger.info(f"entropy is: {entropy}")
    logger.info(f"creative_starting_prompt: {creative_prompt}")
    logger.debug(f"conversation is: {conversation}")

    # this function includes the conversation history
    
    gametext = conversation_gametext_api(entropy, persona_data, conversation, creative_prompt, abstract_concept)
    return gametext


def gen_initial_call_response(entropy, persona, player_gametext):
    # this part of the code goes WAY too slow. Removing the use of nltk for initial generation of the creative_prompt words
    #creative_prompt = create_vars.gen_creative_prompt(create_vars.gen_random_words(entropy), entropy)
    creative_prompt = create_vars.gen_creative_prompt_api(entropy)
    abstract_concept = create_vars.get_abstract_concept()
    lang_device = create_vars.get_lang_device()

    logger.info(f"==========================")
    logger.info(f"persona is: {persona}")
    logger.info(f"lang_device is: {lang_device}")
    logger.info(f"abstract_concept is: {abstract_concept}")
    logger.info(f"entropy is: {entropy}")
    logger.info(f"creative_starting_prompt: {creative_prompt}")

    # this is the path for the match to create gametext
    if player_gametext is not None:
        gametext = reaction_gametext_api(entropy, persona, player_gametext, creative_prompt, abstract_concept)

    # this is the path for the player to create gametext
    if player_gametext is None:
        gametext = initial_gametext_api(entropy, persona, creative_prompt, abstract_concept)

    #logger.info(f"poem result:\n{poem_result}")
    logger.debug(f"poem_gen completed successfully, gametext is {gametext}")
    return gametext

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
        
