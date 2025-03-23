from typing import Optional

from fastapi import FastAPI, Depends, Request, Form, status
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse

from pathlib import Path

from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from jinja2 import Environment, FileSystemLoader

from sqlalchemy.orm import Session

from pydantic import BaseModel

import openpyxl

import models
from Generator import Generator

from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.mount("/static", StaticFiles(directory="static"), name="static")

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("xlsx_template.html")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):  # Add the "request" parameter
    # Render the base.html template
    return templates.TemplateResponse("base.html", {"request": request})


@app.post("/teacher/")
def create_teacher(
        id_l: str = Form(...),
        name: str = Form(...),
        surname: str = Form(...),
        mon: bool = Form(False),
        tue: bool = Form(False),
        wed: bool = Form(False),
        thu: bool = Form(False),
        fri: bool = Form(False),
        db: Session = Depends(get_db)
):
    # Create a new Lecturer object using the form data
    new_teacher = models.Lecturer(
        id_lecturer=id_l,
        name=name,
        surname=surname,
        monday=mon,
        tuesday=tue,
        wednesday=wed,
        thursday=thu,
        friday=fri
    )
    db.add(new_teacher)
    db.commit()


@app.get("/get_teachers")
def get_teachers(db: Session = Depends(get_db)):
    return db.query(models.Lecturer).all()


@app.post("/room/")
def create_room(id_r: str = Form(...),
                has_computers: bool = Form(False),
                db: Session = Depends(get_db)
                ):
    new_room = models.Room(
        id_room=id_r,
        has_computers=has_computers)
    db.add(new_room)
    db.commit()


@app.post("/subject/")
def create_subject(id_s: str = Form(...),
                   name: str = Form(...),
                   study_credits: int = Form(...),
                   needs_computers: bool = Form(False),
                   db: Session = Depends(get_db)):
    new_subject = models.Subject(
        id_subject=id_s,
        name=name,
        study_credits=study_credits,
        needs_computers=needs_computers)
    db.add(new_subject)
    db.commit()


@app.post("/generate/")
def generate_schedule(db: Session = Depends(get_db)):
    # Create an instance of the Generator class with the existing teachers list
    teachers = db.query(models.Lecturer).all()
    subjects = db.query(models.Subject).all()
    rooms = db.query(models.Room).all()

    generator = Generator(subjects, rooms, teachers)
    generator.generate()

    return RedirectResponse(url="/display_xlsx")


@app.post("/display_xlsx", response_class=HTMLResponse)
async def display_xlsx():
    # Read the XLSX file
    xlsx_file = r"C:\Users\sofja\Documents\data.xlsx"  # Replace with your XLSX file path
    wb = openpyxl.load_workbook(xlsx_file)
    sheet = wb.active

    # Extract data from the XLSX file
    data = []
    for row in sheet.iter_rows(values_only=True):
        data.append(row)

    # Render the data using a Jinja2 template
    xlsx_html = template.render(data=data)

    return xlsx_html


# Serve an XLSX file
@app.get("/download_xlsx")
async def download_xlsx():
    file_path = Path(r"C:\Users\sofja\Documents\data.xlsx")
    return FileResponse(file_path,
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=data.xlsx"})
