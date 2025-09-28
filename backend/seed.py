from .database import SessionLocal, engine, Base
from . import models
from .train_model import train_and_save_model
def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # sample users - adapted to students
        s1 = models.Student(student_id=1, age=18, gender='Male', attendance_percentage=85, gpa=7.2, parent_education='Graduate', socioeconomic_status='Medium', extracurricular_participation=1, previous_failures=0, drop_out=0)
        s2 = models.Student(student_id=2, age=19, gender='Female', attendance_percentage=60, gpa=4.1, parent_education='High School', socioeconomic_status='Low', extracurricular_participation=0, previous_failures=2, drop_out=1)
        db.add_all([s1,s2])
        db.commit()
        print("Seeded sample students")
    finally:
        db.close()
if __name__ == "__main__":
    seed()
