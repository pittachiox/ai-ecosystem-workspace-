from db import create_student, create_tables, delete_student, drop_tables, update_student
from db import SessionLocal


def run_tests():
    create_tables()
    print("Created students table")

    with SessionLocal() as session:
        student = create_student(session, name="Alice", age=21, major="Computer Science")
        print("Inserted student:", student.id, student.name, student.age, student.major)

        updated = update_student(session, student.id, age=22, major="Software Engineering")
        print("Updated student:", updated.id, updated.name, updated.age, updated.major)

        deleted = delete_student(session, student.id)
        print("Deleted student:", deleted)

    drop_tables()
    print("Dropped students table")


if __name__ == "__main__":
    run_tests()
