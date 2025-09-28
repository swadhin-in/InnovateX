# Simple script to generate dummy students and POST them to the ingest endpoint
import requests
import random
import json
API = "http://127.0.0.1:8000"
def random_student(i):
    return {
        "student_id": i,
        "age": random.randint(17,25),
        "gender": random.choice(["Male","Female"]),
        "attendance_percentage": round(random.uniform(40,100),1),
        "gpa": round(random.uniform(2.0,9.0),1),
        "parent_education": random.choice(["High School","Graduate","Postgraduate"]),
        "socioeconomic_status": random.choice(["Low","Medium","High"]),
        "extracurricular_participation": random.randint(0,3),
        "previous_failures": random.randint(0,3),
        "drop_out": random.choice([0,1]) if random.random() < 0.3 else None
    }
def main(n=50):
    batch = {"students":[random_student(i) for i in range(1000,1000+n)]}
    res = requests.post(API + "/ingest/students", json=batch)
    print(res.status_code, res.text)
if __name__ == "__main__":
    main(100)
