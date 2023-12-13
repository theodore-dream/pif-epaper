import os
import uuid
import json

from modules.logger import setup_logger
logger = setup_logger("setup_utils")

openai_api_key = os.environ["OPENAI_API_KEY"]

def get_or_create_uuid():
    if os.path.exists('game_state.txt'):
        with open('game_state.txt', 'r') as file:
            game_state = json.load(file)
            game_uuid = game_state.get('uuid', None)
            #logger.info(f"setup_utils - game_uuid found = {game_uuid}")
    else:
        game_uuid = str(uuid.uuid4())
        game_state = {'uuid': game_uuid}
        with open('game_state.txt', 'w') as file:
            json.dump(game_state, file)
            #logger.info(f"setup_utils - game_uuid created = {game_uuid}")

    logger.debug(f"setup_utils - game_uuid is = {game_uuid}")
    return game_uuid

