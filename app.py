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
editors = Jinja2Templates(directory="templates/editors")

app = FastAPI()


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
async def read_root(request: Request):
    return templates.TemplateResponse("admin_view.html", {"request": request})


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
    teachers = db.query(models.Lecturer).all()
    subjects = db.query(models.Subject).all()
    rooms = db.query(models.Room).all()

    generator = Generator(subjects, rooms, teachers)
    generator.generate()

    return RedirectResponse(url="/display_xlsx")


@app.post("/display_xlsx", response_class=HTMLResponse)
async def display_xlsx(request: Request):
    xlsx_file = r"C:\Users\sofja\Documents\data.xlsx"  # replace with your personal XLSX file path
    wb = openpyxl.load_workbook(xlsx_file)
    sheet = wb.active

    # get data from Excel file
    data = []
    for row in sheet.iter_rows(values_only=True):
        data.append(row)

    return templates.TemplateResponse("xlsx_template.html", {"request": request, "data": data})


@app.get("/download_xlsx")
async def download_xlsx():
    file_path = Path(r"C:\Users\sofja\Documents\data.xlsx")
    return FileResponse(file_path,
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=data.xlsx"})


@app.get("/manage_entities/", response_class=HTMLResponse)
async def manage_entities(request: Request, db: Session = Depends(get_db)):
    lecturers = db.query(models.Lecturer).all()
    subjects = db.query(models.Subject).all()
    rooms = db.query(models.Room).all()

    return templates.TemplateResponse("manage_entities.html", {
        "request": request,
        "lecturers": lecturers,
        "rooms": rooms,
        "subjects": subjects,
    })


# Rooms routes
@app.get("/edit_room/{room_id}", response_class=HTMLResponse)
async def edit_room(request: Request, room_id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id_room == room_id).first()
    return editors.TemplateResponse("edit_room.html", {"request": request, "room": room})


@app.post("/update_room/{room_id}")
async def update_room(room_id: int, has_computers: bool = Form(...), db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id_room == room_id).first()
    room.has_computers = has_computers
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete_room/{room_id}")
async def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id_room == room_id).first()
    db.delete(room)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


# Subjects routes
@app.get("/edit_subject/{subject_id}", response_class=HTMLResponse)
async def edit_subject(request: Request, subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(models.Subject).filter(models.Subject.id_subject == subject_id).first()
    return editors.TemplateResponse("edit_subject.html", {"request": request, "subject": subject})


@app.post("/update_subject/{subject_id}")
async def update_subject(
        subject_id: int,
        name: str = Form(...),
        study_credits: int = Form(...),
        needs_computers: bool = Form(...),
        db: Session = Depends(get_db),
):
    subject = db.query(models.Subject).filter(models.Subject.id_subject == subject_id).first()
    subject.name = name
    subject.study_credits = study_credits
    subject.needs_computers = needs_computers
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete_subject/{subject_id}")
async def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(models.Subject).filter(models.Subject.id_subject == subject_id).first()
    db.delete(subject)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


# Lecturers routes
@app.get("/edit_lecturer/{lecturer_id}", response_class=HTMLResponse)
async def edit_lecturer(request: Request, lecturer_id: int, db: Session = Depends(get_db)):
    lecturer = db.query(models.Lecturer).filter(models.Lecturer.id_lecturer == lecturer_id).first()
    return editors.TemplateResponse("edit_lecturer.html", {"request": request, "lecturer": lecturer})


@app.post("/update/{lecturer_id}")
async def update_lecturer(lecturer_id: int, name: str = Form(...), surname: str = Form(...),
                          db: Session = Depends(get_db)):
    lecturer = db.query(models.Lecturer).filter(models.Lecturer.id_lecturer == lecturer_id).first()
    lecturer.name = name
    lecturer.surname = surname
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{lecturer_id}")
async def delete_lecturer(lecturer_id: int, db: Session = Depends(get_db)):
    lecturer = db.query(models.Lecturer).filter(models.Lecturer.id_lecturer == lecturer_id).first()
    db.delete(lecturer)
    db.commit()
    return RedirectResponse(url="/", status_code=303)
