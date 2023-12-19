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
import argparse


# setup GPIO
buttons.setup()

#start logger
logger = setup_logger("main.py")
logger.debug("Logger is set up and running.")

#init our display
epaper_write.init_display()

# to setup command line flags for keyboard or pi
def parse_args():
    parser = argparse.ArgumentParser(description="Start the poetry game with a specified input mode.")
    parser.add_argument("--input-mode", choices=['keyboard', 'pi'], default='keyboard', 
                        help="Specify the input mode: 'keyboard' or 'raspberry'")
    return parser.parse_args()

# this is where the input mode logic goes
def get_input(input_mode):
    if input_mode == 'keyboard':
        print("Press 'l' for left, 'r' for right:")
        while True:
            key = input().lower()
            if key in ['l', 'r']:
                return key
            else:
                print("Invalid input. Please press 'l' for left or 'r' for right.")
    elif input_mode == 'raspberry':
        # Include your Raspberry Pi button logic here
        pass

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
    # TEMP let's test capping this at 0.9
    entropy = min(Decimal('0.85'), entropy + Decimal('0.05'))
    # Return a result (e.g., a string containing game text)
    logger.debug(f"right button pressed")
    return entropy

# maybe flash the entropy level on the screen for a second or two, along with a random persona?
def poetry_game_intro(entropy):
    logger.debug("starting introduction to the game")
    opening_text1 = intro_vars.opening_text1
    
    epaper_write.display_information(opening_text1)
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
    player_gametext = poem_gen.gen_initial_call_response(entropy, player_persona, player_gametext)
    print("-" * 30)
    logger.info(f"player_speech_gen player_gametext is:\n{player_gametext}")
    return player_gametext

# here taking in the player_gametext as input
def match_speech_gen(entropy, match_persona, player_gametext):
    match_gametext = poem_gen.gen_initial_call_response(entropy, match_persona, player_gametext)
    print("-" * 30)
    # already broken here
    logger.info(f"match_speech_gen match_gametext is:\n{match_gametext}")
    return match_gametext

# here taking in the player_gametext as input
def conversation_gametext_gen(entropy, persona_name, persona_data, conversation):
    gametext = poem_gen.gen_conversation(persona_name, entropy, persona_data, conversation)
    print("-" * 30)
    # already broken here
    logger.info(f"{persona_name} conversation_gametext_gen gametext is:\n{gametext}")
    return gametext

def handle_active_session(session_id, player_persona, match_persona, player_persona_name, match_persona_name, conversation_data, player_gametext, match_gametext, session_state, entropy):
    logger.debug("Handling active session...")
    # we are saving the game for the first time or the nth time, ensuring always active if player gets here
    session_state = "active"
    # the data being enteterd into the checkpoint is incorrect 
    logger.info(f"about to do a save checkpoint. Make sure the values are right. session_id, player_persona, match_persona, player_persona_name, match_persona_name, player_gametext, match_gametext, session_state, entropy: {session_id, player_persona, match_persona, player_persona_name, match_persona_name, player_gametext, match_gametext, session_state, entropy}")
    db_service.save_checkpoint_write_to_database(session_id, player_persona, match_persona, player_persona_name, match_persona_name, conversation_data, player_gametext, match_gametext, session_state, entropy)
    #checkpoint saved, session is now active
    #issue now is there is no content to save, I guess it can just be None? 
    return player_gametext, match_gametext

def run_game(player_persona, match_persona, player_persona_name, match_persona_name, conversation_data, session_state, entropy, session_id, input_mode):
    # Entropy modification logic (currently faked for development)
    # this section right here is currently meant to be used with raspberry pi hardware attached buttons that are each coded to be left or right 
    # alternatively, if using keyboard mode, you can use the up and down arrow keys to select "l" or "r" 

    info_gametext = None
    if session_state == "new":
        info_gametext, session_state = handle_new_session(session_id, player_persona, match_persona, player_persona_name, match_persona_name, entropy)
        # displaying the poetry intro game text here... hm. 
        epaper_write.display_information(info_gametext)
        # highlighting the player and match on new game initiation 
        # we want the gametext to be the information about the peronas
        player_gametext = player_persona
        match_gametext = match_persona
        epaper_write.display_dialogue_both(player_gametext, match_gametext, player_persona_name, match_persona_name, entropy, 10)

    # this is the main game loop 
    elif session_state == "active":
        player_gametext = None
        match_gametext = None
        # I think I need this for the first init run possibly? it does change state to active. might be able to get rid of this completely 
        player_gametext, match_gametext = handle_active_session(session_id, player_persona, match_persona, player_persona_name, match_persona_name, conversation_data, player_gametext, match_gametext, session_state, entropy)
        
        # Print instructions before getting input
        print("\nChoose your action:")
        print("Press 'l' to decrease entropy, 'r' to increase entropy. Make your selection and press Enter")

        # here I want to give the player some options and add those options into player_speech_gen api call, need to split those out probably 
        user_input = get_input(input_mode)

        if user_input == 'l':
            entropy = handle_option_l(entropy)
        elif user_input == 'r':
            entropy = handle_option_r(entropy)

        # here I need to have 2 code paths, one where it is the first time we are entering into this main game loop, where there is no match_gametext
        # so here I need to add a conversation_data object 

        if conversation_data is None:
            conversation_data = ""
            # here I want to do two writes, one where I write the first part and then another where I write again and show both dialogues 
            player_gametext = player_speech_gen(float(entropy), player_persona)
            epaper_write.display_dialogue_left(player_gametext, match_gametext, player_persona_name, match_persona_name, entropy, 10)
            # this is designed to append player_gametext, which should be a string, to conversation_data
            # improvement needed is likely to include the name of the person who is speaking somehow 
            conversation_data = player_persona_name + player_gametext + conversation_data 
        
            # here incorporating the player text
            # issue here with the 
            match_gametext = match_speech_gen(float(entropy), match_persona, player_gametext)  
            epaper_write.display_dialogue_both(player_gametext, match_gametext, player_persona_name, match_persona_name, entropy, 10)
            conversation_data = match_persona_name + match_gametext + conversation_data 

        if conversation_data is not None:
            player_gametext = conversation_gametext_gen(float(entropy), "player", player_persona, conversation_data)
            match_gametext = conversation_gametext_gen(float(entropy), "match", match_persona, conversation_data)  
            # this should take the history of what's been said and use it
            epaper_write.display_dialogue_both(player_gametext, match_gametext, player_persona_name, match_persona_name, entropy, 10)
            conversation_data = player_gametext + match_gametext + conversation_data

        db_service.save_checkpoint_write_to_database(session_id, player_persona, match_persona, player_persona_name, match_persona_name, conversation_data, player_gametext, match_gametext, session_state, entropy)


def initialize_new_session(session_id, input_mode):
    logger.debug("Initializing new session...")

    player_personas = intro_vars.select_player_persona()
    match_personas = intro_vars.select_match_persona()

    def get_persona_choice(personas, persona_type, input_mode):
        category, persona_dict = list(personas.items())[0]  # Existing code
        persona_list = list(persona_dict.items())[:5]  # Existing code
        persona_names = '\n'.join([f"{i}. {key}" for i, (key, _) in enumerate(persona_list, start=1)])
        logger.info(f"persona_list is{persona_list}")
        logger.info(f"persona_names is{persona_names}")

        # Display persona names on e-paper
        persona_selection_information = persona_type + " list: \n" + persona_names
        epaper_write.display_information(persona_selection_information)  

        print(f"Select your {persona_type} persona:")
        print(persona_names)
        print("0. Random")

        if input_mode == 'keyboard':
            while True:
                choice = input("Enter your selected number: ")
                if choice.isdigit():
                    choice = int(choice)
                    if 0 <= choice <= len(persona_list):
                        selected_key, selected_desc = persona_list[choice - 1] if choice != 0 else random.choice(persona_list)
                        epaper_write.clear_display()
                        return selected_key, selected_desc
                    else:
                        print("Invalid choice. Please try again.")
                else:
                    print("Invalid input. Please enter a number.")
        elif input_mode == 'raspberry':
            # Implement Raspberry Pi button logic for selecting persona
            # You will need to modify this part to adapt your button logic for selecting options
            pass  # Replace with your Raspberry Pi input logic

        epaper_write.clear_display()

    # Display player personas on e-paper and get choice
    player_persona_name, player_persona = get_persona_choice(player_personas, "player", input_mode)

    # Display match personas on e-paper and get choice
    match_persona_name, match_persona = get_persona_choice(match_personas, "match", input_mode)

    # setup initial entropy and set new session state
    entropy = Decimal(random.randint(30, 45)) / Decimal(100)
    session_state = "new"

    # Display options for different personas here by listing all 5 names 
    epaper_write.display_dialogue_both(player_persona, match_persona, player_persona_name, match_persona_name, entropy, 10)

    logger.info(f"Selected player_persona_name: {player_persona_name}, Description: {player_persona}")
    logger.info(f"Selected match_persona_name: {match_persona_name}, Description: {match_persona}")

    db_service.new_game_init_write_to_database(session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy)
    logger.info(f"New session created with ID: {session_id} and entropy: {entropy}")

    conversation_data = None

    run_game(player_persona, match_persona, player_persona_name, match_persona_name, conversation_data, session_state, entropy, session_id, input_mode)

def continue_active_session(session_data, input_mode):
    session_id, player_persona, match_persona, player_persona_name, match_persona_name, conversation_data, session_state, entropy = session_data
    logger.info(f" Continuing active session. Current state of session_id, player_persona, match_persona, player_persona_name, match_persona_name, conversation_data, session_state, entropy: {session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy}")
    run_game(player_persona, match_persona, player_persona_name, match_persona_name, conversation_data, session_state, entropy, session_id, input_mode)


if __name__ == "__main__":
    args = parse_args()
    input_mode = args.input_mode

    try:
        while True:
            session_id = setup_utils.get_or_create_uuid()
            session_data = db_service.read_from_database(session_id)
            if session_data is not None and session_data[6] == "active":
                continue_active_session(session_data, input_mode)
            else:
                initialize_new_session(session_id, input_mode)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram has been stopped by the user.")
        GPIO.cleanup()



## running notes
## make the display stay on until the next button interaction
## would like to work towards entropy warrior type of setup
## character, has traits, and you gain and lose them, each has a base, and you increasingly get better and better or worse and worse until win or lose 
## need to add code for display cleanup / clean shutdown 