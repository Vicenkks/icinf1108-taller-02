from sqlalchemy import select
from sqlalchemy.orm import Session

from app.pets.pets_model import PetModel


class PetsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all_by_student(self, student_id: str) -> list[PetModel]:
        statement = (
            select(PetModel)
            .where(PetModel.student_id == student_id)
            .order_by(PetModel.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def find_by_id(self, pet_id: str) -> PetModel | None:
        return self.db.get(PetModel, pet_id)

    def find_by_student_and_name(
        self,
        student_id: str,
        name: str,
    ) -> PetModel | None:
        statement = select(PetModel).where(
            PetModel.student_id == student_id,
            PetModel.name == name,
        )
        return self.db.scalar(statement)

    def add(self, pet: PetModel) -> PetModel:
        self.db.add(pet)
        return pet

    def delete(self, pet: PetModel) -> None:
        self.db.delete(pet)