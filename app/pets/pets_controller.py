from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.pets.pets_schemas import CreatePetDto, Pet, PetList, UpdatePetDto
from app.pets.pets_service import PetsService

router = APIRouter(
    prefix="/api/students/{studentId}/pets",
    tags=["Pets"],
)


def get_pets_service(
    db: Session = Depends(get_db),
) -> PetsService:
    return PetsService(db)


@router.get("")
def find_all(
    studentId: str,
    service: PetsService = Depends(get_pets_service),
) -> PetList:
    return service.find_all_for_student(studentId)


@router.post("", status_code=201)
def create(
    studentId: str,
    body: CreatePetDto,
    service: PetsService = Depends(get_pets_service),
) -> Pet:
    return service.create(studentId, body)


@router.patch("/{petId}")
def update(
    studentId: str,
    petId: str,
    body: UpdatePetDto,
    service: PetsService = Depends(get_pets_service),
) -> Pet:
    return service.update(studentId, petId, body)


@router.delete("/{petId}")
def delete(
    studentId: str,
    petId: str,
    service: PetsService = Depends(get_pets_service),
) -> Pet:
    return service.delete(studentId, petId)