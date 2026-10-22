from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.pets.pets_model import PetModel
from app.pets.pets_repository import PetsRepository
from app.pets.pets_schemas import CreatePetDto, Pet, PetList, UpdatePetDto
from app.shared.exceptions import conflict
from app.shared.mappers import pet_to_schema
from app.students.students_repository import StudentsRepository


class PetsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = PetsRepository(db)
        self.students_repository = StudentsRepository(db)

    def find_all_for_student(self, student_id: str) -> PetList:
        self._find_student_or_404(student_id)
        pets = self.repository.find_all_by_student(student_id)

        return PetList(
            total=len(pets),
            items=[pet_to_schema(pet) for pet in pets],
        )

    def create(self, student_id: str, data: CreatePetDto) -> Pet:
        self._find_student_or_404(student_id)
        self.assert_no_conflicts(student_id, data)

        pet = PetModel(
            student_id=student_id,
            name=data.name,
            species=data.species,
            age=data.age,
        )

        self.repository.add(pet)
        self.db.commit()
        self.db.refresh(pet)

        return pet_to_schema(pet)

    def update(self, student_id: str, pet_id: str, data: UpdatePetDto) -> Pet:
        pet = self._find_owned_or_404(student_id, pet_id)
        self.assert_no_conflicts(student_id, data, except_id=pet_id)

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(pet, field, value)

        self.db.commit()
        self.db.refresh(pet)

        return pet_to_schema(pet)

    def delete(self, student_id: str, pet_id: str) -> Pet:
        pet = self._find_owned_or_404(student_id, pet_id)
        result = pet_to_schema(pet)

        self.repository.delete(pet)
        self.db.commit()

        return result

    def _find_student_or_404(self, student_id: str) -> None:
        if self.students_repository.find_by_id(student_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

    def _find_owned_or_404(self, student_id: str, pet_id: str) -> PetModel:
        self._find_student_or_404(student_id)

        pet = self.repository.find_by_id(pet_id)
        if pet is None or pet.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada",
            )

        return pet

    def assert_no_conflicts(
        self,
        student_id: str,
        data: CreatePetDto | UpdatePetDto,
        except_id: str | None = None,
    ) -> None:
        if not data.name:
            return

        existing = self.repository.find_by_student_and_name(student_id, data.name)

        if existing and existing.id != except_id:
            raise conflict(
                {"name": {"message": "Ya tienes una mascota con ese nombre"}}
            )