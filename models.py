from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    url: str = Field(max_length=500)
    repo_url: Optional[str] = Field(default=None, max_length=500)


class Visitor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    device_type: str = Field(default="Unknown", max_length=20)
    user_agent: Optional[str] = Field(default=None, max_length=512)


class Profile(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    name: str = Field(default="Roberto Schneider", max_length=100)
    role: str = Field(default="Desenvolvedor Full Stack", max_length=100)
    description: str = Field(default="Apaixonado por tecnologia e inovação.", max_length=2000)
    location: str = Field(default="Brasil", max_length=100)
    stacks: str = Field(default="Python, JavaScript, SQL", max_length=500)
    photo_url: Optional[str] = Field(default=None, max_length=500)
    social_linkedin: Optional[str] = Field(default=None, max_length=500)
    social_github: Optional[str] = Field(default=None, max_length=500)
