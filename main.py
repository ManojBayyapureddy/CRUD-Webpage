from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Column, String
from database import engine, SessionLocal, Base
from models import User

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="templates")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


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
    # Dynamic SQL to add column
    try:
        with engine.connect() as conn:
            conn.execute(f'ALTER TABLE users ADD COLUMN IF NOT EXISTS "{column_name}" TEXT;')
            conn.commit()
    except Exception as e:
        print("Error adding column:", e)
    return RedirectResponse("/", status_code=303)
