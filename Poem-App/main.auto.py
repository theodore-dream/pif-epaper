from modules.logger import setup_logger
from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
import openai
from modules import openai_api_service, db_service, setup_utils, poem_gen, display_write, intro_vars
import datetime
import random
from decimal import Decimal, ROUND_DOWN
from time import sleep
import uuid
import time

#start logger
logger = setup_logger("main.py")
logger.debug("Logger is set up and running.")

# maybe flash the entropy level on the screen for a second or two, along with a random persona?
def poetry_game_intro(entropy):
    logger.debug("starting introduction")
    opening_text1 = intro_vars.opening_text1
    opening_text2 = intro_vars.opening_text2 
    opening_text3  = intro_vars.opening_text3 
    
    display_write.display_write(opening_text1, 5)
    display_write.display_write(opening_text2, 2)
    display_write.display_write(opening_text3, 1)
    logger.debug("opening text written to luma")
    creative_prompt = "Welcome the player to the poetry game in a single sentence. Welcome them in an such a way that is unexpected, smug, or pedantic"
    api_response = openai_api_service.openai_api_call("", creative_prompt, entropy)
    # this is the text that gets saved to the DB, I guess whatever is custom
    logger.info("poetry_game_intro api response: " + api_response)
    gametext = api_response 
    return gametext

def poetry_gen_loop(entropy):
    # check current entropy level
    #api_response = openai_api_service.openai_api_call("", creative_prompt, entropy)
    #level_text = "Your poem is " + api_response + "--end poem--"
    gametext = poem_gen.parse_response(entropy)
    logger.debug(f"gametext is: {gametext}")
    return gametext

def handle_option_a(entropy):
    # Implement game logic for Option A
    # Decrease entropy by .05, not going below 0
    entropy = max(Decimal('0.0'), entropy - Decimal('0.05'))
    # Return a result (e.g., a string containing game text)
    return entropy
    

def handle_option_b(entropy):
    # Implement game logic for Option B
    # Increase entropy by .05, not going above 1
    #entropy = min(1.0, float(entropy) + 0.1)
    entropy = min(Decimal('1.0'), entropy + Decimal('0.05'))
    # Return a result (e.g., a string containing game text)
    return entropy
    

def run_game(persona, session_state, gametext, entropy, session_id):
    # running game 
    # first lets get the game status 

    #if choice is None:
    #    # this is a do nothing option, just wait for the user to make a choice A or B" 
    #    sleep(1)
    #    print("waiting for user to make a choice...")
    #    logger.info("logger reporting, waiting for user to make a choice...")

    # Run the intro function or the poetry loop 
    if session_state == "new":
        logger.debug(f"new session identified. poetry game intro starting now...")
        gametext = poetry_game_intro(entropy)
        session_state = "active"
        db_service.write_to_database(session_id, session_state, entropy)
        
    elif session_state == "active":
        logger.debug(f"runing poetry_gen_loop, current entropy is: {entropy}")
        gametext = poetry_gen_loop(float(entropy))
        db_service.write_to_database(session_id, session_state, entropy)

    # placeholder 
    choice = "Option B"

    if choice == "Option A":
        entropy = handle_option_a(entropy)
        logger.debug(f"Option A chosen. entropy decreased by .05. Current entropy level: {entropy}")
        db_service.write_to_database(session_id, session_state, entropy)
    
    elif choice == "Option B":
        entropy = handle_option_b(entropy)
        logger.debug(f"Option B chosen. entropy increased by .05. Current entropy level: {entropy}")
        db_service.write_to_database(session_id, session_state, entropy)


    # Save the updated game state to the database
    #db_service.save_game(session_id, level, entropy)
    #logger.debug(f"saving updated game state, state is currently session, level, entropy: {session_id, level, entropy}")

    # Return the updated game text data to luma to display on the screen
    display_write.display_write(gametext, 30)
    logger.debug("gametext is: " + gametext)


def maintain_game_state():
    # latest game status
    logger.debug("running game status check....")

    # check for ID on filesystem, very rudementary version of a config file/system
    # can only create new sessions for first implementation, not resume old ones
    session_id = setup_utils.get_or_create_uuid()
    logger.debug("session_id found or generated = " + session_id)

    # temporarily for all new games, no initial session state
    logger.debug(f"reading session data from DB: {session_id}")
    session_data = db_service.read_from_database(session_id)
    logger.debug (f"session data from DB: {session_data}")
    
    # the second variable in the tuple is the session state
    if session_data is not None and session_data[1] == "active":
        persona, session_state, gametext, entropy, session_id = session_data
    else:
        # no session found, initialize values
        logger.debug(f"no active session found, initialize values, creating new session with state: new")
        persona = None
        session_state = "new"
        gametext = None
        # entropy is a random decimal from 0.00 to 1.00 with 1-2 decimal places
        #entropy = Decimal(str(random.uniform(0.0, 0.9))).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        entropy = Decimal(random.randint(0, 90)) / Decimal(100)

        # save this new game state before proceeding .. 
        db_service.write_to_database(session_id, session_state, entropy)
        logger.info(f"new session created with entropy: {entropy}")


    logger.info(
        "Session data setup before running game - Session ID: {}, Persona: {}, Session State: {}, Game Text: {}, Entropy: {}".format(
            session_id, persona, session_state, gametext, entropy
        )
    )

    # lets run the game
    run_game(persona, session_state, gametext, entropy, session_id)
    #return persona, session_state, gametext, entropy, session_id, 

if __name__ == "__main__":
   
   try:
        while True:
            maintain_game_state()
            time.sleep(1)  # optional delay if you want to run the function with intervals
   except KeyboardInterrupt:
            print("\nProgram has been stopped by the user.")

# main interaction is just left and right button increasing and decreasing entropy 

