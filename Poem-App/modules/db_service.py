import psycopg2
from psycopg2 import Error
from modules.logger import setup_logger

logger = setup_logger("db_service")

def write_to_database(session_id, session_state, entropy):
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
        logger.debug(f"Completed insert INSERT INTO poem_game (session_id, session_state, entropy): {session_id, session_state, entropy} on session: {session_id}")
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
        query = f"SELECT persona, session_state, gametext, entropy, session_id FROM poem_game WHERE session_id = %s ORDER BY tstz DESC LIMIT 1"
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
                   (None if result is None else result[4])
        else:
            return result[0], result[1], result[2], result[3], result[4]

    except (Exception, Error) as error:
        logger.error("Error while reading column from PostgreSQL", error)
        return None, None, None, None, None


