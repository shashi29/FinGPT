# app/database.py

import psycopg2
from configparser import ConfigParser

def get_database_connection():
    config = ConfigParser()
    config.read('app/config.ini')  # Assuming config file is in the 'app' directory
    db_config = config['database']

    conn = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )

    return conn
