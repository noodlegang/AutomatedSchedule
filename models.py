from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Lecturer(Base):
    __tablename__ = "lecturers"

    id_lecturer = Column("idLecturer", Integer, primary_key=True)
    name = Column("name", String)
    surname = Column("surname", String)
    MON = Column("mondays", Boolean)
    TUE = Column("tuesdays", Boolean)
    WED = Column("wednesdays", Boolean)
    THU = Column("thursdays", Boolean)
    FRI = Column("fridays", Boolean)

    schedules = relationship('Schedule', back_populates='lecturers')

    def __init__(self, id_lecturer, name, surname, monday, tuesday,
                 wednesday, thursday, friday):
        self.id_lecturer = id_lecturer
        self.name = name
        self.surname = surname
        self.MON = monday
        self.TUE = tuesday
        self.WED = wednesday
        self.THU = thursday
        self.FRI = friday

    def __repr__(self):
        return f"({self.id_lecturer}) {self.name} {self.surname}"

    def __returnID__(self):
        return f"{self.id_lecturer}"


class Schedule(Base):
    __tablename__ = "schedules"

    id_schedule = Column("idSchedule", Integer, primary_key=True)
    id_room = Column("idRoom", Integer, ForeignKey("rooms.idRoom"))
    id_lecturer = Column("idLecturer", Integer, ForeignKey("lecturers.idLecturer"))
    id_subject = Column("idSubject", Integer, ForeignKey("subjects.idSubject"))

    lecturers = relationship('Lecturer', back_populates='schedules')
    rooms = relationship('Room', back_populates='schedules')
    subjects = relationship('Subject', back_populates='schedules')

    def __init__(self, id_schedule, id_room, id_lecturer, id_subject):
        self.id_lecturer = id_lecturer
        self.id_schedule = id_schedule
        self.id_subject = id_subject
        self.id_room = id_room

    def __returnID__(self):
        return f"{self.id_schedule}"


class Room(Base):
    __tablename__ = "rooms"

    id_room = Column("idRoom", Integer, primary_key=True)
    has_computers = Column("hasComputers", Boolean)

    schedules = relationship('Schedule', back_populates='rooms')

    def __init__(self, id_room, has_computers):
        self.id_room = id_room
        self.has_computers = has_computers

    def __returnID__(self):
        return f"{self.id_room}"


class Subject(Base):
    __tablename__ = "subjects"

    id_subject = Column("idSubject", Integer, primary_key=True)
    name = Column("name", String)
    study_credits = Column("credits", Integer)
    needs_computers = Column("needsComputers", Boolean)

    schedules = relationship('Schedule', back_populates='subjects')

    def __init__(self, id_subject, name, study_credits, needs_computers):
        self.id_subject = id_subject
        self.name = name
        self.needs_computers = needs_computers
        self.study_credits = study_credits

    def __returnID__(self):
        return f"{self.id_subject}"
