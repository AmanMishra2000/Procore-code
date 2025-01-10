from fastapi import FastAPI
from app.routes import project
from fastapi.middleware.cors import CORSMiddleware
from app.middleware import add_security_headers
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Apply middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sandbox.procore.com/4267423/company/home"],  # Update with allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers
app.middleware("http")(add_security_headers)

# Include routers
app.include_router(project.router)

@app.get("/")
def health_check():
    return {"message": "API is running!"}
