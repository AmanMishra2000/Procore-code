from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Project
from ..schemas import ProjectCreate
import os
import requests

router = APIRouter()

PROCORE_API_BASE = os.getenv("PROCORE_API_BASE")
PROCORE_CLIENT_ID = os.getenv("PROCORE_CLIENT_ID")
PROCORE_CLIENT_SECRET = os.getenv("PROCORE_CLIENT_SECRET")

def get_procore_access_token():
    # Fetch the access token from Procore
    response = requests.post(
        f"{PROCORE_API_BASE}/oauth/token",
        data={
            "client_id": PROCORE_CLIENT_ID,
            "client_secret": PROCORE_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]

@router.get("/import-projects/{company_id}")
def import_projects(company_id: int, db: Session = Depends(get_db)):
    token = get_procore_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{PROCORE_API_BASE}/projects?company_id={company_id}", headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch projects")

    projects_data = response.json()
    for project in projects_data:
        db_project = Project(
            procore_id=project["id"],
            name=project["name"],
            status=project["status"],
            start_date=project.get("start_date"),
            end_date=project.get("end_date"),
        )
        db.merge(db_project)  # Update if exists, else insert
    db.commit()
    return {"message": "Projects imported successfully"}
