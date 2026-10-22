from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)
from app.students.students_service import StudentsService

router = APIRouter(prefix="/api/students", tags=["Students"])


def get_students_service(
    db: Session = Depends(get_db),
) -> StudentsService:
    return StudentsService(db)


@router.get("")
def find_all(
    service: StudentsService = Depends(get_students_service),
) -> StudentList:
    return service.find_all()


@router.get("/{studentId}")
def find_by_id(
    studentId: str,
    service: StudentsService = Depends(get_students_service),
) -> Student:
    return service.find_by_id(studentId)


@router.post("", status_code=201)
def create(
    body: CreateStudentDto,
    service: StudentsService = Depends(get_students_service),
) -> Student:
    return service.create(body)


@router.patch("/{studentId}")
def update(
    studentId: str,
    body: UpdateStudentDto,
    service: StudentsService = Depends(get_students_service),
) -> Student:
    return service.update(studentId, body)


@router.delete("/{studentId}")
def delete(
    studentId: str,
    service: StudentsService = Depends(get_students_service),
) -> Student:
    return service.delete(studentId)