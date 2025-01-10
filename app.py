from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import os
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

app = FastAPI()

class Project(BaseModel):
    id: int
    name: str
    status: str

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Parse the DATABASE_URL using urlparse for easier extraction of components
url = urlparse(DATABASE_URL)

# Prepare the db_config dictionary for psycopg2 connection
db_config = {
    "dbname": url.path[1:],  # dbname is after the first slash
    "user": url.username,
    "password": url.password,
    "host": url.hostname,
    "port": url.port,
}

def connect_db():
    try:
        # Establish the database connection using psycopg2
        return psycopg2.connect(**db_config)
    except psycopg2.Error as err:
        print(f"Database connection error: {err}")
        raise HTTPException(status_code=500, detail="Database connection error")

@app.on_event("startup")
def init_db():
    # Initialize the database on startup (e.g., create the table if not exists)
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL
        )
    """)
    db.commit()
    cursor.close()
    db.close()

@app.post("/import_project")
def import_project(project: Project):
    print(f"Received project: {project}")  # This will show the incoming data for debugging
    db = connect_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO projects (id, name, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name, status = EXCLUDED.status
        """, (project.id, project.name, project.status))
        db.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to import project")
    finally:
        cursor.close()
        db.close()

    return {"message": "Project imported successfully", "project": project}

@app.get("/get_project/{project_id}")
def get_project(project_id: int):
    # Endpoint to get project by ID
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()
    cursor.close()
    db.close()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"id": project[0], "name": project[1], "status": project[2]}

@app.get("/")
def health_check():
    # Simple health check endpoint
    return {"message": "API is running!"} 