from app.pets.pets_model import PetModel
from app.pets.pets_schemas import Pet
from app.students.students_model import StudentModel
from app.students.students_schemas import Student


def student_to_schema(student: StudentModel) -> Student:
    return Student(
        id=student.id,
        name=student.name,
        username=student.username,
        email=student.email,
        age=student.age,
        createdAt=student.created_at,
        updatedAt=student.updated_at,
    )


def pet_to_schema(pet: PetModel) -> Pet:
    return Pet(
        id=pet.id,
        studentId=pet.student_id,
        name=pet.name,
        species=pet.species,
        age=pet.age,
        createdAt=pet.created_at,
        updatedAt=pet.updated_at,
    )