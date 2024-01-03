import psycopg2
from configparser import ConfigParser

def get_database_connection():
    config = ConfigParser()
    config.read('config.ini')
    db_config = config['database']

    conn = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )

    return conn

def create_tables(conn):
    with conn.cursor() as cursor:
        # Define the table creation SQL statements
        create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                password VARCHAR(255),
                client_number VARCHAR(3),
                customer_number VARCHAR(10)
            );
        """

        create_boards_table = """
            CREATE TABLE IF NOT EXISTS boards (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                client_number VARCHAR(3),
                customer_number VARCHAR(10)
            );
        """

        create_documents_table = """
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                board_id INTEGER REFERENCES boards(id),
                name VARCHAR(255),
                size INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                client_number VARCHAR(3),
                customer_number VARCHAR(10)
            );
        """

        create_prompts_table = """
            CREATE TABLE IF NOT EXISTS prompts (
                id SERIAL PRIMARY KEY,
                board_id INTEGER REFERENCES boards(id),
                prompt_text TEXT,
                prompt_out TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                client_number VARCHAR(3),
                customer_number VARCHAR(10)
            );
        """

        # Execute table creation SQL statements
        cursor.execute(create_users_table)
        cursor.execute(create_boards_table)
        cursor.execute(create_documents_table)
        cursor.execute(create_prompts_table)

    # Commit the changes
    conn.commit()

def close_connection(conn):
    conn.close()

def main():
    try:
        # Get a database connection
        conn = get_database_connection()

        # Create tables
        create_tables(conn)

        # Close the connection
        close_connection(conn)

        print("Tables created successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
