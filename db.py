import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse
import os

# Parse the DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

url = urlparse(DATABASE_URL)

db_config = {
    "dbname": url.path[1:],
    "user": url.username,
    "password": url.password,
    "host": url.hostname,
    "port": url.port,
}

def connect_db():
    try:
        return psycopg2.connect(**db_config)
    except psycopg2.Error as e:
        raise ConnectionError(f"Database connection error: {e}")

def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
