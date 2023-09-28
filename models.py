from sqlalchemy import Boolean, Column, Integer, String, ForeignKey

from database import Base


class Lecturer(Base):
    __tablename__ = "lecturers"

    idLecturer = Column("idLecturer", Integer, primary_key=True)
    name = Column("name", String)
    surname = Column("surname", String)
    MON = Column("mondays", Boolean)
    TUE = Column("tuesdays", Boolean)
    WED = Column("wednesdays", Boolean)
    THU = Column("thursdays", Boolean)
    FRI = Column("fridays", Boolean)

    def __init__(self, idLecturer, name, surname):
        self.idLecturer = idLecturer
        self.name = name
        self.surname = surname

    def __repr__(self):
        return f"({self.idLecturer}) {self.name} {self.surname}"

    def __returnID__(self):
        return f"{self.idLecturer}"


class Schedule(Base):
    __tablename__ = "schedules"

    idSchedule = Column("idSchedule", Integer, primary_key=True)
    idRoom = Column("idRoom", Integer, ForeignKey("rooms.idRoom"))
    idLecturer = Column("idLecturer", Integer, ForeignKey("lecturers.idLecturer"))
    idPlan = Column("idPlan", Integer, ForeignKey("plans.idPlan"))

    def __init__(self, idSchedule, idRoom, idLecturer, idPlan):
        self.idLecturer = idLecturer
        self.idSchedule = idSchedule
        self.idPlan = idPlan
        self.idRoom = idRoom

    def __returnID__(self):
        return f"{self.idSchedule}"


class Room(Base):
    __tablename__ = "rooms"

    idRoom = Column("idRoom", Integer, primary_key=True)
    name = Column("name", Integer)
    hasComputers = Column("hasComputers", Boolean)

    def __init__(self, idRoom, name, hasComputers):
        self.idRoom = idRoom
        self.hasComputers = hasComputers
        self.name = name

    def __returnID__(self):
        return f"{self.idRoom}"


class Group(Base):
    __tablename__ = "groups"

    idGroup = Column("idGroup", Integer, primary_key=True)
    name = Column("name", String)

    def __init__(self, idGroup, name):
        self.idGroup = idGroup
        self.name = name

    def __returnID__(self):
        return f"{self.idGroup}"


class Plan(Base):
    __tablename__ = "plans"

    idPlan = Column("idPlan", Integer, primary_key=True)
    idSubject = Column("idSubject", Integer, ForeignKey("subjects.idSubject"))
    idRoom = Column("idRoom", Integer, ForeignKey("rooms.idRoom"))
    credits = Column("credits", Integer)

    def __init__(self, idPlan, idSubject, idRoom, credits):
        self.idSubject = idSubject
        self.idPlan = idPlan
        self.idRoom = idRoom
        self.credits = credits

    def __returnID__(self):
        return f"{self.idPlan}"


class Subject(Base):
    __tablename__ = "subjects"

    idSubject = Column("idSubject", Integer, primary_key=True)
    name = Column("name", String)

    def __init__(self, idSubject, name):
        self.idSubject = idSubject
        self.name = name

    def __returnID__(self):
        return f"{self.idSubject}"
