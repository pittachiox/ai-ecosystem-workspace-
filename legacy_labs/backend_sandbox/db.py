from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    major = Column(String(100), nullable=False)


engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def drop_tables():
    Base.metadata.drop_all(bind=engine)


def create_student(session: Session, name: str, age: int, major: str) -> Student:
    student = Student(name=name, age=age, major=major)
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


from typing import Optional


def update_student(session: Session, student_id: int, **fields) -> Optional[Student]:
    student = session.get(Student, student_id)
    if student is None:
        return None
    for name, value in fields.items():
        setattr(student, name, value)
    session.commit()
    session.refresh(student)
    return student


def delete_student(session: Session, student_id: int) -> bool:
    student = session.get(Student, student_id)
    if student is None:
        return False
    session.delete(student)
    session.commit()
    return True
