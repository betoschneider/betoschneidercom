from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    url: str
    repo_url: Optional[str] = None


class Visitor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    device_type: str = "Unknown"  # "PC" or "Smartphone"
    user_agent: Optional[str] = None


class Profile(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    name: str = "Roberto Schneider"
    role: str = "Desenvolvedor Full Stack"
    description: str = "Apaixonado por tecnologia e inovação."
    location: str = "Brasil"
    stacks: str = "Python, JavaScript, SQL"
    photo_url: Optional[str] = None
    social_linkedin: Optional[str] = None
    social_github: Optional[str] = None
