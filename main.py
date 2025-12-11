import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Project

load_dotenv()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "changeme")

app = FastAPI(title="Linktree-like API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", include_in_schema=False)
def root():
    return FileResponse("static/index.html")


@app.get("/admin", include_in_schema=False)
def admin_page():
    return FileResponse("static/admin.html")


@app.get("/projects")
def read_projects():
    with Session(engine) as session:
        projects = session.exec(select(Project)).all()
        return projects


def check_admin_token(x_admin_token: str = Header(None)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/projects", dependencies=[Depends(check_admin_token)])
def create_project(project: Project):
    with Session(engine) as session:
        session.add(project)
        session.commit()
        session.refresh(project)
        return project


@app.put("/projects/{project_id}", dependencies=[Depends(check_admin_token)])
def update_project(project_id: int, project: Project):
    with Session(engine) as session:
        db = session.get(Project, project_id)
        if not db:
            raise HTTPException(404, "Not found")
        db.title = project.title
        db.description = project.description
        db.url = project.url
        session.add(db)
        session.commit()
        session.refresh(db)
        return db


@app.delete("/projects/{project_id}", dependencies=[Depends(check_admin_token)])
def delete_project(project_id: int):
    with Session(engine) as session:
        db = session.get(Project, project_id)
        if not db:
            raise HTTPException(404, "Not found")
        session.delete(db)
        session.commit()
        return {"ok": True}
