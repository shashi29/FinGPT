import os

from google.cloud.sql.connector import Connector, IPTypes
import pg8000

import sqlalchemy
from sqlalchemy import inspect

def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    """Initializes a Unix socket connection pool for a Cloud SQL instance of Postgres."""
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_user = 'postgres'  # e.g. 'my-database-user'
    db_pass = 'a55zWlt:CYtAi|FB(|jJSpRA90N}'  # e.g. 'my-database-password'
    db_name = 'collaborativedocsdb_test'  # e.g. 'my-database'
    unix_socket_path = 'independent-way-410316:us-central1:collaborativedocsdb-test'   # e.g. '/cloudsql/project:region:instance'
    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            unix_socket_path,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type
        )
        return conn

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # [START_EXCLUDE]
        # Pool size is the maximum number of permanent connections to keep.
        pool_size=5,
        # Temporarily exceeds the set pool_size if no connections are available.
        max_overflow=2,
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        pool_timeout=30,  # 30 seconds
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # re-established
        pool_recycle=1800,  # 30 minutes
        # [END_EXCLUDE]
    )
    return pool

def show_tables(engine):
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

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_users_table))
        conn.execute(sqlalchemy.text(create_boards_table))
        conn.execute(sqlalchemy.text(create_documents_table))
        conn.execute(sqlalchemy.text(create_prompts_table))
        conn.commit()
engine = connect_unix_socket()
    
# Example: Show tables in the connected database
show_tables(engine)

# Close the engine (optional)
engine.dispose()