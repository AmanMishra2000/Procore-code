from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .database import Base

class Project(Base):
    __tablename__ = "Projects_tb"  # Set the table name explicitly

    id = Column(Integer, primary_key=True, index=True)
    procore_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    status = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
