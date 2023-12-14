from modules.logger import setup_logger
from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
import openai
from modules import openai_api_service, db_service, setup_utils, poem_gen, epaper_write, intro_vars, buttons
import datetime
import random
from decimal import Decimal, ROUND_DOWN
from time import sleep
import uuid
import time
import RPi.GPIO as GPIO

# setup GPIO
buttons.setup()

#start logger
logger = setup_logger("main.py")
logger.debug("Logger is set up and running.")

#init our display
epaper_write.init_display()

def player_poetry_gen(entropy, player_persona):    
    player_gametext = poem_gen.parse_response(entropy, player_persona)
    print("-" * 30)
    logger.info(f"player_poetry_gen player_gametext is:\n{player_gametext}")
    return player_gametext

def match_poetry_gen(entropy, match_persona):
    match_gametext = poem_gen.parse_response(entropy, match_persona)
    print("-" * 30)
    logger.info(f"match_poetry_gen match_gametext is:\n{match_gametext}")
    return match_gametext

def handle_option_l(entropy):
    # Implement game logic for Option A
    # Decrease entropy by .05, not going below 0
    entropy = max(Decimal('0.0'), entropy - Decimal('0.05'))
    # Return a result (e.g., a string containing game text)
    logger.debug(f"left button pressed")
    return entropy

def handle_option_r(entropy):
    # Implement game logic for Option B
    # Increase entropy by .05, not going above 1
    #entropy = min(1.0, float(entropy) + 0.1)
    # TEMP let's test capping this at 0.6
    entropy = min(Decimal('0.95'), entropy + Decimal('0.05'))
    # Return a result (e.g., a string containing game text)
    logger.debug(f"right button pressed")
    return entropy

# maybe flash the entropy level on the screen for a second or two, along with a random persona?
def poetry_game_intro(entropy):
    logger.debug("starting introduction to the game")
    opening_text1 = intro_vars.opening_text1
    #opening_text2 = intro_vars.opening_text2 
    #opening_text3  = intro_vars.opening_text3 
    
    epaper_write.display_information(opening_text1, 3)
    #epaper_write.display_information(opening_text2, 3)
    #epaper_write.display_information(opening_text3, 1)
    logger.debug("opening text written to epaper")
    opening_poem = intro_vars.introduction_generation_api(entropy)
    # this is the text that gets saved to the DB, I guess whatever is custom
    return opening_poem

# gametext is not used in the database, its just the intro gametext
def handle_new_session(session_id, player_persona, match_persona, entropy):
    logger.debug("Handling new session...")
    info_gametext = poetry_game_intro(entropy)
    session_state = "active"
    db_service.new_game_init_write_to_database(session_id, player_persona, match_persona, session_state, entropy)
    return info_gametext, session_state

def handle_active_session(session_id, player_persona, match_persona, entropy):
    logger.debug("Handling active session...")
    player_gametext = player_poetry_gen(float(entropy), player_persona)
    match_gametext = match_poetry_gen(float(entropy), match_persona)  # Replace with actual logic when available
    session_state = "active"
    db_service.save_checkpoint_write_to_database(session_id, player_persona, match_persona, player_gametext, match_gametext, session_state, entropy)
    #checkpoint saved
    logger.info(f"checkpoint saved. session_id, player_persona, match_persona, player_gametext, match_gametext, session_state, entropy: {session_id, player_persona, match_persona, player_gametext, match_gametext, session_state, entropy}.")
    return player_gametext, match_gametext

def run_game(player_persona, match_persona, session_state, entropy, session_id):
    # Entropy modification logic (currently faked for development)
    entropy = handle_option_r(entropy)

    info_gametext = None
    if session_state == "new":
        info_gametext, session_state = handle_new_session(session_id, player_persona, match_persona, entropy)
        epaper_write.display_information(info_gametext, 10)
        # assigning the variable for the gametext to the persona data to display information about each
        player_gametext = player_persona
        match_gametext = match_persona 
        player_persona_words = player_persona.split()
        player_name = ' '.join(player_persona_words[:1])    
        match_persona_words = match_persona.split()
        match_name = ' '.join(match_persona_words[:1])    
        # highlighting the player and match on new game initiation 
        epaper_write.display_dialogue(player_gametext, match_gametext, player_name, match_name, entropy, 10)

    elif session_state == "active":
        player_gametext, match_gametext = handle_active_session(session_id, player_persona, match_persona, entropy)
        # Split the persona strings into words
        player_persona_words = player_persona.split()
        match_persona_words = match_persona.split()
        # Select the first three words and join them back into a string
        player_name = ' '.join(player_persona_words[:1])
        match_name = ' '.join(match_persona_words[:1])
        logger.info
        logger.info(f"player_name is: {player_name}, match_name is: {match_name}")
        epaper_write.display_dialogue(player_gametext, match_gametext, player_name, match_name, entropy, 10)

def initialize_new_session(session_id):
    logger.debug("Initializing new session...")
    player_persona = intro_vars.select_persona()
    match_persona = intro_vars.select_persona()
    session_state = "new"
    gametext = None
    entropy = Decimal(random.randint(0, 20)) / Decimal(100)
    db_service.new_game_init_write_to_database(session_id, player_persona, match_persona, session_state, entropy)
    logger.info(f"New session created with ID: {session_id} and entropy: {entropy}")
    run_game(player_persona, match_persona, session_state, entropy, session_id)


def continue_active_session(session_data):
    player_persona, match_persona, session_state, gametext, entropy, session_id = session_data
    logger.info(f" Continuing active session. Current state of player_persona, match_persona, session_state, gametext, entropy, session_id: {player_persona, match_persona, session_state, gametext, entropy, session_id}")
    run_game(player_persona, match_persona, session_state, entropy, session_id)

def check_game_state():
    logger.debug("Running game status check...")

    session_id = setup_utils.get_or_create_uuid()
    logger.debug(f"Session ID found or generated: {session_id}")

    session_data = db_service.read_from_database(session_id)
    logger.debug(f"Session data from DB: {session_data}")

    if session_data is not None and session_data[2] == "active":
        continue_active_session(session_data)
    else:
        initialize_new_session(session_id)


if __name__ == "__main__":
    try:
        while True:
            check_game_state()
            time.sleep(0.1)  # optional delay
    except KeyboardInterrupt:
        print("\nProgram has been stopped by the user.")
        GPIO.cleanup()



if __name__ == "__main__":
   
   try:
        while True:
            check_game_state()
            time.sleep(0.1)  # optional delay if you want to run the function with intervals
   except KeyboardInterrupt:
        print("\nProgram has been stopped by the user.")
        GPIO.cleanup()  # cleanup GPIO pins once on exit
# main interaction is just left and right button increasing and decreasing entropy 

## running notes
## make the display stay on until the next button interaction
## would like to work towards entropy warrior type of setup
## character, has traits, and you gain and lose them, each has a base, and you increasingly get better and better or worse and worse until win or lose 
## need to add code for display cleanup / clean shutdown 