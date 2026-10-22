from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.pets.pets_model import PetModel
from app.pets.pets_repository import PetsRepository
from app.shared.exceptions import conflict
from app.shared.mappers import student_to_schema
from app.shared.types import FieldErrors
from app.students.students_model import StudentModel
from app.students.students_repository import StudentsRepository
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)


class StudentsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = StudentsRepository(db)
        self.pets_repository = PetsRepository(db)

    def find_all(self) -> StudentList:
        students = self.repository.find_all()
        return StudentList(
            total=len(students),
            items=[student_to_schema(student) for student in students],
        )

    def find_by_id(self, student_id: str) -> Student:
        return student_to_schema(self._find_model_or_404(student_id))

    def create(self, data: CreateStudentDto) -> Student:
        self.assert_no_conflicts(data)

        seen_pet_names: set[str] = set()
        for pet in data.pets:
            if pet.name in seen_pet_names:
                raise conflict(
                    {"name": {"message": "Ya tienes una mascota con ese nombre"}}
                )
            seen_pet_names.add(pet.name)

        student = StudentModel(
            name=data.name,
            username=data.username,
            email=str(data.email),
            age=data.age,
        )

        for pet_data in data.pets:
            student.pets.append(
                PetModel(
                    name=pet_data.name,
                    species=pet_data.species,
                    age=pet_data.age,
                )
            )

        try:
            self.repository.add(student)
            self.db.commit()
            self.db.refresh(student)
        except IntegrityError as error:
            self.db.rollback()
            raise conflict(
                {
                    "email": {
                        "message": "El correo electrónico o nombre de usuario ya está en uso"
                    }
                }
            ) from error

        return student_to_schema(student)

    def update(self, student_id: str, data: UpdateStudentDto) -> Student:
        student = self._find_model_or_404(student_id)
        self.assert_no_conflicts(data, except_id=student_id)

        values = data.model_dump(exclude_none=True)
        if "email" in values:
            values["email"] = str(values["email"])

        for field, value in values.items():
            setattr(student, field, value)

        try:
            self.db.commit()
            self.db.refresh(student)
        except IntegrityError as error:
            self.db.rollback()
            raise conflict(
                {
                    "email": {
                        "message": "El correo electrónico o nombre de usuario ya está en uso"
                    }
                }
            ) from error

        return student_to_schema(student)

    def delete(self, student_id: str) -> Student:
        student = self._find_model_or_404(student_id)
        result = student_to_schema(student)

        self.repository.delete(student)
        self.db.commit()

        return result

    def _find_model_or_404(self, student_id: str) -> StudentModel:
        student = self.repository.find_by_id(student_id)

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

        return student

    def assert_no_conflicts(
        self,
        data: CreateStudentDto | UpdateStudentDto,
        except_id: str | None = None,
    ) -> None:
        errors: FieldErrors = {}

        if data.email:
            existing = self.repository.find_by_email(str(data.email))
            if existing and existing.id != except_id:
                errors["email"] = {"message": "El correo electrónico ya está en uso"}

        if data.username:
            existing = self.repository.find_by_username(data.username)
            if existing and existing.id != except_id:
                errors["username"] = {"message": "El nombre de usuario ya está en uso"}

        if errors:
            raise conflict(errors)