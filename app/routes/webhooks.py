from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Project
from hashlib import sha256
import hmac
import os

router = APIRouter()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

def verify_webhook_signature(payload, signature):
    calculated_signature = hmac.new(
        WEBHOOK_SECRET.encode(), payload, sha256
    ).hexdigest()
    return hmac.compare_digest(calculated_signature, signature)

@router.post("/webhook")
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    signature = request.headers.get("X-Procore-Signature")
    payload = await request.body()

    if not verify_webhook_signature(payload, signature):
        return {"error": "Invalid webhook signature"}

    data = await request.json()
    event = data.get("event")
    project_data = data.get("resource")
    
    if event == "project.create":
        new_project = Project(
            procore_id=project_data["id"],
            name=project_data["name"],
            status=project_data["status"],
            start_date=project_data.get("start_date"),
            end_date=project_data.get("end_date"),
        )
        db.add(new_project)
    elif event == "project.update":
        existing_project = db.query(Project).filter(Project.procore_id == project_data["id"]).first()
        if existing_project:
            existing_project.name = project_data["name"]
            existing_project.status = project_data["status"]
            db.add(existing_project)
    elif event == "project.delete":
        existing_project = db.query(Project).filter(Project.procore_id == project_data["id"]).first()
        if existing_project:
            existing_project.is_deleted = True
            db.add(existing_project)

    db.commit()
    return {"message": "Webhook processed"}
