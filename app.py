from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import os
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

app = FastAPI()

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Project(BaseModel):
    id: int
    name: str

class ProjectResponse(BaseModel):
    id: int
    name: str

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Parse the DATABASE_URL
url = urlparse(DATABASE_URL)

# Database configuration
db_config = {
    "dbname": url.path[1:],  # dbname is after the first slash
    "user": url.username,
    "password": url.password,
    "host": url.hostname,
    "port": url.port,
}

def connect_db():
    try:
        return psycopg2.connect(**db_config)
    except psycopg2.Error as err:
        print(f"Database connection error: {err}")
        raise HTTPException(status_code=500, detail="Database connection error")

@app.on_event("startup")
def init_db():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Procoreprojects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """)
    db.commit()
    cursor.close()
    db.close()

@app.post("/import_project", dependencies=[Depends(oauth2_scheme)])
def import_project(project: Project, token: str = Depends(oauth2_scheme)):
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO Procoreprojects (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name
        """, (project.id, project.name))
        db.commit()
    except psycopg2.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import project: {e}")
    finally:
        cursor.close()
        db.close()
    return {"message": "Project imported successfully", "project": project.dict()}

@app.get("/get_project/{project_id}", response_model=ProjectResponse, dependencies=[Depends(oauth2_scheme)])
def get_project(project_id: int, token: str = Depends(oauth2_scheme)):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM Procoreprojects WHERE id = %s", (project_id,))
    project = cursor.fetchone()
    cursor.close()
    db.close()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"id": project[0], "name": project[1]}

@app.get("/gets_project", response_model=list[ProjectResponse], dependencies=[Depends(oauth2_scheme)])
def gets_project(token: str = Depends(oauth2_scheme)):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM Procoreprojects")
    projects = cursor.fetchall()
    cursor.close()
    db.close()
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")
    return [{"id": proj[0], "name": proj[1]} for proj in projects]

@app.get("/")
def health_check():
    return {"message": "API is running!"}
