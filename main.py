import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import engine, SessionLocal, Base
from models import User
  # your SQLAlchemy models

# ------------------- DATABASE SETUP -------------------
DATABASE_URL = os.environ.get("DATABASE_URL")  # Render internal URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------- FASTAPI APP -------------------
app = FastAPI()

# Templates
templates = Jinja2Templates(directory="templates")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ------------------- STARTUP EVENT -------------------
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# ------------------- ROUTES -------------------
@app.get("/")
def home(request: Request):
    session = SessionLocal()
    users = session.query(User).all()
    session.close()
    return templates.TemplateResponse("index.html", {"request": request, "users": users})

@app.post("/add/")
def add_user(name: str = Form(...), email: str = Form(...),
             phone: str = Form(""), address: str = Form("")):
    session = SessionLocal()
    user = User(name=name, email=email, phone=phone, address=address)
    session.add(user)
    session.commit()
    session.close()
    return RedirectResponse("/", status_code=303)

@app.post("/update/")
def update_user(id: int = Form(...), name: str = Form(...),
                email: str = Form(...), phone: str = Form(""), address: str = Form("")):
    session = SessionLocal()
    user = session.query(User).filter(User.id == id).first()
    if user:
        user.name = name
        user.email = email
        user.phone = phone
        user.address = address
        session.commit()
    session.close()
    return RedirectResponse("/", status_code=303)

@app.post("/delete/")
def delete_user(id: int = Form(...)):
    session = SessionLocal()
    user = session.query(User).filter(User.id == id).first()
    if user:
        session.delete(user)
        session.commit()
    session.close()
    return RedirectResponse("/", status_code=303)

@app.post("/add-column/")
def add_column(column_name: str = Form(...)):
    try:
        with engine.connect() as conn:
            conn.execute(f'ALTER TABLE users ADD COLUMN IF NOT EXISTS "{column_name}" TEXT;')
            conn.commit()
    except Exception as e:
        print("Error adding column:", e)
    return RedirectResponse("/", status_code=303)

# ------------------- LOCAL RUN -------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
