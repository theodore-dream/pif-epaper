import psycopg2
from uuid import uuid4
import time
from psycopg2 import Error
from psycopg2 import OperationalError


try:
    connection = psycopg2.connect(dbname="postgres",
                              host="localhost",
                              user="pi",
                              password="raspberry",
                              port = "5432",
                              connect_timeout=3)

    connection.autocommit = True

    # Debugging information
    print("Connected to the Postgres database successfully")

    # Create a new database called "Poems" if it doesn't already exist
    cur = connection.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname='game'")
    exists = cur.fetchone()

    if exists:
        print("Database already exists")
    else:
        cur.execute("CREATE DATABASE game;")
        print("game Database created successfully")

    # Close the cursor and connection to "postgres"
    cur.close()
    connection.close()

    # Connect to the new "Poems" database
    connection = psycopg2.connect(dbname="game",
                              host="localhost",
                              user="pi",
                              password="raspberry",
                              port = "5432",
                              connect_timeout=3)

    connection.autocommit = True

    # Debugging information
    print("Connected to the game database successfully")

    cursor = connection.cursor()
    # this line is to ensure UUID support is in place
    cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

    # check if the table exists
    cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='poem_game')")
    table_exists = cursor.fetchone()[0]

    if table_exists:
        print("poem_game already exists in PostgreSQL")
    else:
        # SQL query to create a new table
        create_table_query = '''
        CREATE TABLE poem_game (
            id SERIAL PRIMARY KEY,
            session_id uuid DEFAULT uuid_generate_v4 (),
            tstz timestamp DEFAULT current_timestamp,
            player_persona VARCHAR,
            match_persona VARCHAR,
            player_persona_name VARCHAR,
            match_persona_name VARCHAR,
            session_state VARCHAR,
            gametext VARCHAR,
            player_gametext VARCHAR,
            match_gametext VARCHAR,
            entropy DECIMAL(3, 2),
            level NUMERIC(3, 0)
        );
        CREATE INDEX idx_poem_game ON poem_game (session_id, tstz DESC);
        '''
        # Execute a command: this creates a new table
        cursor.execute(create_table_query)
        connection.commit()
        print("Table created successfully in PostgreSQL")

except OperationalError as e:
    print("Operational Error:", e)

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:
    # Close the cursor and connection
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()

    # Debugging information
    print("PostgreSQL connection is closed")
