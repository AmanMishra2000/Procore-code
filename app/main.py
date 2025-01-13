from fastapi import FastAPI
from .routes import projects, webhooks
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
