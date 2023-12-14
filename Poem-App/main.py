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
    
    epaper_write.display_information(opening_text1, 3)
    logger.debug("opening text written to epaper")
    opening_poem = intro_vars.introduction_generation_api(entropy)
    # this is the text that gets saved to the DB, I guess whatever is custom
    return opening_poem

# gametext is not used in the database, its just the intro gametext
def handle_new_session(session_id, player_persona, match_persona, player_persona_name, match_persona_name, entropy):
    logger.debug("Handling new session...")
    info_gametext = poetry_game_intro(entropy)
    session_state = "active"
    db_service.new_game_init_write_to_database(session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy)
    return info_gametext, session_state

def player_speech_gen(entropy, player_persona):    
    # there is no gametext because we are creating it here
    player_gametext = None
    player_gametext = poem_gen.parse_response(entropy, player_persona, player_gametext)
    print("-" * 30)
    logger.info(f"player_speech_gen player_gametext is:\n{player_gametext}")
    return player_gametext

# here taking in the player_gametext as input
def match_speech_gen(entropy, match_persona, player_gametext):
    match_gametext = poem_gen.parse_response(entropy, match_persona, player_gametext)
    print("-" * 30)
    logger.info(f"match_speech_gen match_gametext is:\n{match_gametext}")
    return match_gametext

def handle_active_session(session_id, player_persona, player_persona_name, match_persona_name, player_gametext, match_gametext, match_persona, entropy):
    logger.debug("Handling active session...")
    # we are saving the game for the first time or the nth time, ensuring always active if player gets here
    session_state = "active"
    db_service.save_checkpoint_write_to_database(session_id, player_persona, match_persona, player_persona_name, match_persona_name, player_gametext, match_gametext, session_state, entropy)
    #checkpoint saved, session is now active
    #issue now is there is no content to save, I guess it can just be None? 
    logger.info(f"checkpoint saved. session_id, player_persona, match_persona, player_gametext, match_gametext, session_state, entropy: {session_id, player_persona, match_persona, player_gametext, match_gametext, session_state, entropy}.")
    return player_gametext, match_gametext

def run_game(player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy, session_id):
    # Entropy modification logic (currently faked for development)
    entropy = handle_option_r(entropy)

    info_gametext = None
    if session_state == "new":
        info_gametext, session_state = handle_new_session(session_id, player_persona, match_persona, player_persona_name, match_persona_name, entropy)
        # displaying the poetry intro game text here... hm. 
        epaper_write.display_information(info_gametext, 10)
        # highlighting the player and match on new game initiation 
        # we want the gametext to be the information about the peronas
        player_gametext = player_persona
        match_gametext = match_persona
        epaper_write.display_dialogue_both(player_gametext, match_gametext, player_persona_name, match_persona_name, entropy, 10)

    # this is the main game loop 
    elif session_state == "active":
        player_gametext = None
        match_gametext = None
        player_gametext, match_gametext = handle_active_session(session_id, player_persona, player_persona_name, match_persona_name, player_gametext, match_gametext, match_persona, entropy)
        
        # here I want to give the player some options and add those options into player_speech_gen api call, need to split those out probably 
        
        # here I want to do two writes, one where I write the first part and then another where I write again and show both dialogues 
        player_gametext = player_speech_gen(float(entropy), player_persona)
        epaper_write.display_dialogue_left(player_gametext, match_gametext, player_persona_name, match_persona_name, entropy, 10)

        # here incorporating the player text
        match_gametext = match_speech_gen(float(entropy), match_persona, player_gametext)  
        epaper_write.display_dialogue_both(player_gametext, match_gametext, player_persona_name, match_persona_name, entropy, 10)

def initialize_new_session(session_id):
    logger.debug("Initializing new session...")
    # need to work on a way to allow the player to select the persona 
    player_persona_name, player_persona = intro_vars.select_persona()
    match_persona_name, match_persona = intro_vars.select_persona()
    logger.info(f"player_persona_name: {player_persona_name}")
    logger.info(f"match_persona_name: {match_persona_name}")
    session_state = "new"
    gametext = None
    entropy = Decimal(random.randint(0, 20)) / Decimal(100)
    db_service.new_game_init_write_to_database(session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy)
    logger.info(f"New session created with ID: {session_id} and entropy: {entropy}")
    run_game(player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy, session_id)


def continue_active_session(session_data):
    session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy = session_data
    logger.info(f" Continuing active session. Current state of session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy: {session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy}")
    run_game(player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy, session_id)

def check_game_state():
    logger.debug("Running game status check...")

    session_id = setup_utils.get_or_create_uuid()
    logger.debug(f"Session ID found or generated: {session_id}")

    session_data = db_service.read_from_database(session_id)
    logger.info(f"Session data from DB: {session_data}")

    if session_data is not None and session_data[5] == "active":
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