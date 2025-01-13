from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    procore_id: int
    name: str
    status: str
    start_date: Optional[str]
    end_date: Optional[str]
