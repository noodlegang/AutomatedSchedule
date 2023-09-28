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

    def __init__(self, id_lecturer, name, surname):
        self.id_lecturer = id_lecturer
        self.name = name
        self.surname = surname

    def __repr__(self):
        return f"({self.id_lecturer}) {self.name} {self.surname}"

    def __returnID__(self):
        return f"{self.id_lecturer}"


class Schedule(Base):
    __tablename__ = "schedules"

    id_schedule = Column("idSchedule", Integer, primary_key=True)
    id_room = Column("idRoom", Integer, ForeignKey("rooms.idRoom"))
    id_lecturer = Column("idLecturer", Integer, ForeignKey("lecturers.idLecturer"))
    id_plan = Column("idPlan", Integer, ForeignKey("plans.idPlan"))

    lecturer = relationship('Lecturer', back_populates='schedules')
    room = relationship('Room', back_populates='schedules')
    plan = relationship('Plan', back_populates='schedules')

    def __init__(self, id_schedule, id_room, id_lecturer, id_plan):
        self.id_lecturer = id_lecturer
        self.id_schedule = id_schedule
        self.id_plan = id_plan
        self.id_room = id_room

    def __returnID__(self):
        return f"{self.id_schedule}"


class Room(Base):
    __tablename__ = "rooms"

    id_room = Column("idRoom", Integer, primary_key=True)
    name = Column("name", Integer)
    has_computers = Column("hasComputers", Boolean)

    def __init__(self, id_room, name, has_computers):
        self.id_room = id_room
        self.has_computers = has_computers
        self.name = name

    def __returnID__(self):
        return f"{self.id_room}"


class Plan(Base):
    __tablename__ = "plans"

    id_plan = Column("idPlan", Integer, primary_key=True)
    id_subject = Column("idSubject", Integer, ForeignKey("subjects.idSubject"))
    id_room = Column("idRoom", Integer, ForeignKey("rooms.idRoom"))
    study_credits = Column("credits", Integer)

    room = relationship('Room', back_populates='plans')
    subject = relationship('Subject', back_populates='plans')

    def __init__(self, id_plan, id_subject, id_room, study_credits):
        self.id_subject = id_subject
        self.id_plan = id_plan
        self.id_room = id_room
        self.study_credits = study_credits

    def __returnID__(self):
        return f"{self.id_plan}"


class Subject(Base):
    __tablename__ = "subjects"

    id_subject = Column("idSubject", Integer, primary_key=True)
    name = Column("name", String)
    id_lecturer = Column("idLecturer", Integer, ForeignKey("lecturers.idLecturer"))

    lecturer = relationship('Lecturer', back_populates='subject')

    def __init__(self, id_subject, name, id_lecturer):
        self.id_subject = id_subject
        self.name = name
        self.id_lecturer = id_lecturer

    def __returnID__(self):
        return f"{self.id_subject}"
