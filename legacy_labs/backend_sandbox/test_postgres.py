from db import SessionLocal, Student
from db import create_student, create_tables, delete_student, drop_tables, update_student


def run_tests():
    print("--- Step 1: Create Table 'students' ---")
    create_tables()
    print("Table 'students' created successfully.\n")

    with SessionLocal() as session:
        print("--- Step 2: Inserting Data ---")
        students = [
            ("Bob", 20, "Computer Engineering"),
            ("Beeb", 19, "Information Technology"),
            ("Anna", 22, "Data Science"),
            ("Tom", 23, "Software Engineering"),
        ]

        for name, age, major in students:
            student = create_student(session, name=name, age=age, major=major)
            print(f"Successfully inserted: {student.name} (Major: {student.major})")

        print("\n--- Step 3: Updating Data ---")
        bob = session.query(Student).filter_by(name="Bob").first()
        if bob:
            original_age = bob.age
            original_major = bob.major
            updated = update_student(session, bob.id, age=21, major="Computer Science")
            print(f"Original Age: {original_age}, Major: {original_major}")
            print(f"Updated to Age: {updated.age}, Major: {updated.major}")

        print("\n--- Step 4: Deleting Data ---")
        deleted = delete_student(session, bob.id) if bob else False
        print(f"Deleted student: {bob.name}" if deleted else "Student not deleted.")
        remaining = session.query(Student).all()
        print("Students remaining in DB:", [student.name for student in remaining])

    print("\n--- Step 5: Deleting Table 'students' ---")
    drop_tables()
    print("Table 'students' deleted (dropped) successfully.")


if __name__ == "__main__":
    run_tests()
