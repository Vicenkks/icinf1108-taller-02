from sqlalchemy import select
from sqlalchemy.orm import Session

from app.students.students_model import StudentModel


class StudentsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self) -> list[StudentModel]:
        statement = select(StudentModel).order_by(StudentModel.created_at.desc())
        return list(self.db.scalars(statement).all())

    def find_by_id(self, student_id: str) -> StudentModel | None:
        return self.db.get(StudentModel, student_id)

    def find_by_email(self, email: str) -> StudentModel | None:
        statement = select(StudentModel).where(StudentModel.email == email)
        return self.db.scalar(statement)

    def find_by_username(self, username: str) -> StudentModel | None:
        statement = select(StudentModel).where(StudentModel.username == username)
        return self.db.scalar(statement)

    def add(self, student: StudentModel) -> StudentModel:
        self.db.add(student)
        return student

    def delete(self, student: StudentModel) -> None:
        self.db.delete(student)