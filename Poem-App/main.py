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

# maybe flash the entropy level on the screen for a second or two, along with a random persona?
def poetry_game_intro(entropy):
    logger.debug("starting introduction")
    opening_text1 = intro_vars.opening_text1
    opening_text2 = intro_vars.opening_text2 
    opening_text3  = intro_vars.opening_text3 
    
    epaper_write.display_information(opening_text1, 3)
    epaper_write.display_information(opening_text2, 3)
    epaper_write.display_information(opening_text3, 1)
    logger.debug("opening text written to epaper")
    creative_prompt = "Welcome the player to the poetry game in a single sentence. Welcome them in an such a way that is unexpected, smug, or pedantic"
    api_response = openai_api_service.openai_api_call("", creative_prompt, entropy)
    # this is the text that gets saved to the DB, I guess whatever is custom
    logger.info("poetry_game_intro api response: " + api_response)
    gametext = api_response 
    return gametext

def player_poetry_gen(entropy, player_persona):
    # check current entropy level
    #api_response = openai_api_service.openai_api_call("", creative_prompt, entropy)
    #level_text = "Your poem is " + api_response + "--end poem--"
    player_gametext = poem_gen.parse_response(entropy, player_persona)
    logger.debug(f"player_gametext is: {player_gametext}")
    return player_gametext

def match_poetry_gen(entropy):
    match_gametext = poem_gen.parse_response(entropy)
    logger.debug(f"match_poetry_gen is: {match_poetry_gen}")
    return match_poetry_gen

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
    entropy = min(Decimal('0.6'), entropy + Decimal('0.05'))
    # Return a result (e.g., a string containing game text)
    logger.debug(f"right button pressed")
    return entropy
    

def run_game(player_persona, match_persona, session_state, gametext, entropy, session_id):
    # running game 
    # first lets get the game status 

    #if choice is None:
    #    # this is a do nothing option, just wait for the user to make a choice A or B" 
    #    sleep(1)
    #    print("waiting for user to make a choice...")
    #    logger.info("logger reporting, waiting for user to make a choice...")

    # Handle button presses
    print("button press....")

    # temporarily faking the buttons for development reasons
    entropy = handle_option_r(entropy)
    #pressed = buttons.handle_button_presses(session_id, session_state, entropy)

    # Modify entropy based on button pressed
   #if pressed == "L":
   #     entropy = handle_option_l(entropy)
   # elif pressed == "R":
   #     entropy = handle_option_r(entropy)

    # Run the intro function or the poetry loop 
    if session_state == "new":
        logger.debug(f"new session identified. poetry game intro starting now...")
        gametext = poetry_game_intro(entropy)
        session_state = "active"
        player_persona = None
        match_persona = None
        # this updates session state from new to active
        db_service.game_init_write_to_database(session_id, player_persona, match_persona, session_state, entropy)
        
    elif session_state == "active":
        logger.debug(f"running player_poetry_gen, current entropy is: {entropy}")
        player_gametext = player_poetry_gen(float(entropy), player_persona)
        # placeholder until logic is added 
        match_gametext = "blah blah blah"
        #match_gametext = match_poetry_gen(float(entropy))
        db_service.save_checkpoint_write_to_database(session_id, player_persona, match_persona, player_gametext, match_gametext, session_state, entropy)

    # Save the updated game state to the database
    #db_service.save_game(session_id, level, entropy)
    #logger.debug(f"saving updated game state, state is currently session, level, entropy: {session_id, level, entropy}")

    # Return the updated game text data to display on the screen
    epaper_write.display_information(player_gametext, 7)
    logger.debug("player_gametext is: " + player_gametext)
    logger.debug("mach_gametext is: " + match_gametext)

def check_game_state():
    logger.debug("running game status check....")

    session_id = setup_utils.get_or_create_uuid()
    logger.debug("session_id found or generated = " + session_id)

    logger.debug(f"reading session data from DB: {session_id}")
    session_data = db_service.read_from_database(session_id)
    logger.debug(f"session data from DB: {session_data}")


    state_test = session_data[2]
    logger.info(f"state_test is: {state_test}")

    if session_data is not None and session_data[2] == "active":
        player_persona, match_persona, session_state, gametext, entropy, session_id = session_data
    else:
        logger.debug("no active session found, initialize values, creating new session with state: new")
        
        # we're going to randomly create player and match personas 
        player_persona = intro_vars.select_persona()
        match_persona = intro_vars.select_persona()
        session_state = "new"
        gametext = None
        entropy = Decimal(random.randint(0, 20)) / Decimal(100)

        db_service.game_init_write_to_database(session_id, player_persona, match_persona, session_state, entropy)
        logger.info(f"new session created with entropy: {entropy}")

    logger.info(
        "Session data setup before running game - Session ID: {}, Persona: {}, Session State: {}, Game Text: {}, Entropy: {}".format(
            session_id, player_persona, session_state, gametext, entropy
        )
    )

    # lets run the game
    run_game(player_persona, match_persona, session_state, gametext, entropy, session_id)
    #return persona, session_state, gametext, entropy, session_id, 

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