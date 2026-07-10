import os
import secrets
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from sqlmodel import Session, select, SQLModel, Field
from database import engine, create_db_and_tables
from models import Project, Visitor, Profile

# Carrega .env de múltiplos locais (em ordem de prioridade)
# 1. /var/www/.env (produção em servidor)
# 2. .env (desenvolvimento local)
load_dotenv("/var/www/.env", override=False)
load_dotenv(".env", override=False)

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
if not ADMIN_TOKEN:
    print("ERROR: ADMIN_TOKEN environment variable is required!", file=sys.stderr)
    sys.exit(1)

app = FastAPI(title="Linktree-like API")

class Tool(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: str
    description: Optional[str] = None
    icon: Optional[str] = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://betoschneider.com", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Auto-migration for repo_url (only if column doesn't exist)
    import sqlite3
    try:
        conn = sqlite3.connect('projects.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(project)")
        columns = [col[1] for col in cursor.fetchall()]
        if "repo_url" not in columns:
            cursor.execute("ALTER TABLE project ADD COLUMN repo_url TEXT")
            conn.commit()
            print("Auto-migration: Added repo_url column.")
        conn.close()
    except Exception as e:
        print(f"Auto-migration unexpected error: {e}")


@app.get("/", include_in_schema=False)
def root():
    return FileResponse("static/index.html")


@app.get("/admin", include_in_schema=False)
def admin_page():
    return FileResponse("static/index.html", headers={"X-Robots-Tag": "noindex, nofollow"})


@app.get("/sobre")
def about_page():
    return FileResponse("static/index.html")

@app.get("/ferramentas")
def tools_page():
    return FileResponse("static/index.html")


@app.get("/cv")
def cv_page():
    return FileResponse("static/index.html", headers={"X-Robots-Tag": "noindex, nofollow"})


@app.get("/robots.txt", include_in_schema=False)
def robots_txt():
    return FileResponse("static/robots.txt")


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml():
    return FileResponse("static/sitemap.xml")

def check_admin_token(x_admin_token: str = Header(None)):
    if x_admin_token is None or not secrets.compare_digest(x_admin_token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/projects")
def read_projects():
    with Session(engine) as session:
        projects = session.exec(select(Project)).all()
        return projects

@app.get("/tools")
def read_tools():
    with Session(engine) as session:
        tools = session.exec(select(Tool)).all()
        return tools

@app.post("/tools", dependencies=[Depends(check_admin_token)])
def create_tool(tool: Tool):
    with Session(engine) as session:
        session.add(tool)
        session.commit()
        session.refresh(tool)
        return tool

@app.put("/tools/{tool_id}", dependencies=[Depends(check_admin_token)])
def update_tool(tool_id: int, tool: Tool):
    with Session(engine) as session:
        db_tool = session.get(Tool, tool_id)
        if not db_tool:
            raise HTTPException(404, "Not found")
        db_tool.name = tool.name
        db_tool.url = tool.url
        db_tool.description = tool.description
        db_tool.icon = tool.icon
        session.add(db_tool)
        session.commit()
        session.refresh(db_tool)
        return db_tool

@app.delete("/tools/{tool_id}", dependencies=[Depends(check_admin_token)])
def delete_tool(tool_id: int):
    with Session(engine) as session:
        db_tool = session.get(Tool, tool_id)
        if not db_tool:
            raise HTTPException(404, "Not found")
        session.delete(db_tool)
        session.commit()
        return {"ok": True}

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "geolocation=()")
    response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self' https://betoschneider.com")
    return response


@app.post("/projects", dependencies=[Depends(check_admin_token)])
def create_project(project: Project):
    if not project.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    with Session(engine) as session:
        session.add(project)
        session.commit()
        session.refresh(project)
        return project


@app.put("/projects/{project_id}", dependencies=[Depends(check_admin_token)])
def update_project(project_id: int, project: Project):
    if not project.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    with Session(engine) as session:
        db = session.get(Project, project_id)
        if not db:
            raise HTTPException(404, "Not found")
        db.title = project.title
        db.description = project.description
        db.url = project.url
        db.repo_url = project.repo_url
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


# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)


@app.get("/admin/stats", dependencies=[Depends(check_admin_token)])
@limiter.limit("10/minute")
def get_stats(request: Request):
    with Session(engine) as session:
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)

        statement = select(Visitor).where(Visitor.timestamp >= ninety_days_ago)
        results = session.exec(statement).all()

        stats: Dict[str, Any] = {}

        for visitor in results:
            date_str = visitor.timestamp.strftime("%Y-%m-%d")
            if date_str not in stats:
                stats[date_str] = {"total": 0, "pc": 0, "smartphone": 0}

            stats[date_str]["total"] += 1
            if visitor.device_type == "Smartphone":
                stats[date_str]["smartphone"] += 1
            else:
                stats[date_str]["pc"] += 1

        sorted_stats = []
        for date_key in sorted(stats.keys()):
            entry = stats[date_key]
            entry["date"] = date_key
            sorted_stats.append(entry)

        return sorted_stats


@app.get("/profile")
def get_profile():
    with Session(engine) as session:
        profile = session.get(Profile, 1)
        if not profile:
            # Create default profile if not exists
            profile = Profile(id=1)
            session.add(profile)
            session.commit()
            session.refresh(profile)
        return profile


@app.put("/profile", dependencies=[Depends(check_admin_token)])
def update_profile(new_data: Profile):
    with Session(engine) as session:
        profile = session.get(Profile, 1)
        if not profile:
            profile = Profile(id=1)
            session.add(profile)
        
        # Update fields
        profile.name = new_data.name
        profile.role = new_data.role
        profile.description = new_data.description
        profile.location = new_data.location
        profile.stacks = new_data.stacks
        profile.photo_url = new_data.photo_url
        profile.social_linkedin = new_data.social_linkedin
        profile.social_github = new_data.social_github
        
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile


@app.post("/visit")
def track_visit(request: Request, user_agent: str = Header(None)):
    if not user_agent:
        user_agent = "Unknown"
    user_agent = user_agent[:512]
    
    device_type = "PC"
    ua_lower = user_agent.lower()
    if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
        device_type = "Smartphone"
        
    visitor = Visitor(
        device_type=device_type,
        user_agent=user_agent
    )
    
    with Session(engine) as session:
        session.add(visitor)
        session.commit()
    
    return {"status": "ok"}

