import psycopg2
from psycopg2 import Error
from modules.logger import setup_logger

logger = setup_logger("db_service")

# all this does is ensure the game state moves forward from new game to active game and shows intro screen 
# this approach broke my game, going to try not using it 
def new_game_active_write_to_database(session_id, session_state, entropy):
    try:
        connection = psycopg2.connect(
            dbname="game",
            host="localhost",
            user="pi",
            password="raspberry",
            port="5432",
            connect_timeout=3,
        )
        cursor = connection.cursor()
        query = f"INSERT INTO poem_game (session_id, session_state, entropy) VALUES (%s, %s, %s)"
        cursor.execute(query, (session_id, session_state, entropy))
        logger.debug(f"Executing write txn: {query} on session: {session_id}")
        logger.debug(f"Completed insert INSERT INTO poem_game (session_id, session_state, entropy): {session_id, session_state, entropy}")
        connection.commit()
        logger.debug("Insert committed successfully")
        cursor.close()
        connection.close()
    except (Exception, Error) as error:
        logger.error("Error while inserting in PostgreSQL", error)

# this saves a newly created game and assigns the personas 
def new_game_init_write_to_database(session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy):
    try:
        connection = psycopg2.connect(
            dbname="game",
            host="localhost",
            user="pi",
            password="raspberry",
            port="5432",
            connect_timeout=3,
        )
        cursor = connection.cursor()
        query = f"INSERT INTO poem_game (session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy))
        logger.debug(f"Executing write txn: {query} on session: {session_id}")
        logger.debug(f"Completed insert INSERT INTO poem_game (session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy): {session_id, player_persona, match_persona, player_persona_name, match_persona_name, session_state, entropy}")
        connection.commit()
        logger.debug("Insert committed successfully")
        cursor.close()
        connection.close()
    except (Exception, Error) as error:
        logger.error("Error while inserting in PostgreSQL", error)


# for conversational use, storing the actual messages 
def save_checkpoint_write_to_database(session_id, player_persona, match_persona, player_persona_name, match_persona_name, player_gametext, match_gametext, session_state, entropy):
    try:
        connection = psycopg2.connect(
            dbname="game",
            host="localhost",
            user="pi",
            password="raspberry",
            port="5432",
            connect_timeout=3,
        )
        cursor = connection.cursor()
        query = f"INSERT INTO poem_game (session_id, player_persona, match_persona, player_persona_name, match_persona_name, player_gametext, match_gametext, session_state, entropy) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (session_id, player_persona, player_persona_name, match_persona_name, match_persona, player_gametext, match_gametext, session_state, entropy))
        logger.debug(f"Executing write txn: {query} on session: {session_id}")
        logger.debug(f"Completed insert INSERT INTO poem_game (session_id, player_persona, match_persona, player_persona_name, match_persona_name, player_gametext, match_gametext, session_state, entropy): {session_id, player_persona, match_persona, player_persona_name, match_persona_name, player_gametext, match_gametext, session_state, entropy}")
        connection.commit()
        logger.debug("Insert committed successfully")
        cursor.close()
        connection.close()
    except (Exception, Error) as error:
        logger.error("Error while inserting in PostgreSQL", error)


def save_game(session_id, session_state, entropy):
    try:
        connection = psycopg2.connect(
            dbname="game",
            host="localhost",
            user="pi",
            password="raspberry",
            port="5432",
            connect_timeout=3,
        )
        cursor = connection.cursor()
        query = "UPDATE poem_game SET level = %s, entropy = %s WHERE session_id = %s"
        cursor.execute(query, (session_state, entropy, session_id))
        logger.debug(f"Completed insert INSERT INTO poem_game (session_id, session_state, entropy): {session_id, session_state, entropy} on session: {session_id}")
        connection.commit()
        logger.debug("Insert committed successfully")
        cursor.close()
        connection.close()
    except (Exception, Error) as error:
        logger.error("Error while inserting in PostgreSQL", error)

def read_from_database(session_id):
    try:
        connection = psycopg2.connect(
            dbname="game",
            host="localhost",
            user="pi",
            password="raspberry",
            port="5432",
            connect_timeout=3,
        )
        cursor = connection.cursor()
        query = f"SELECT player_persona, match_persona, player_persona_name, match_persona_name, session_state, gametext, entropy, session_id FROM poem_game WHERE session_id = %s ORDER BY tstz DESC LIMIT 1"
        logger.debug(f"Executing query: {query} on session: {session_id}")
        cursor.execute(query, (session_id,))
        result = cursor.fetchone()
        logger.debug(f"Query executed successfully, result: {result}")
        cursor.close()
        connection.close()
        if result is None:
            return (None if result is None else result[0]), \
                   (None if result is None else result[1]), \
                   (None if result is None else result[2]), \
                   (None if result is None else result[3]), \
                   (None if result is None else result[4]), \
                   (None if result is None else result[5]), \
                   (None if result is None else result[6]), \
                   (None if result is None else result[7]), 
        else:
            return result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7]

    except (Exception, Error) as error:
        logger.error("Error while reading column from PostgreSQL", error)
        return None, None, None, None, None



