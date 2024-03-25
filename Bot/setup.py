import os
import psycopg2
import logging
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import DictCursor
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

dbname = os.getenv("SQL_DATABASE")
user = os.getenv("SQL_USER")
password = os.getenv("SQL_PASSWORD")
host = os.getenv("SQL_HOST")


def setup_database():
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            cursor_factory=DictCursor,
        )
        cur = conn.cursor()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn, cur
    except psycopg2.OperationalError as e:
        logging.error(f"Error in database connection: {e}")
        exit(1)
