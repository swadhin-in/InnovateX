# Example: call /predict with a sample student
import requests
API = "http://127.0.0.1:8000"
def predict_sample():
    payload = {"students":[{"student_id":9999,"age":20,"gender":"Male","attendance_percentage":55,"gpa":5.0,"parent_education":"High School","socioeconomic_status":"Low","extracurricular_participation":0,"previous_failures":1}]}
    res = requests.post(API + "/predict", json=payload)
    print(res.status_code, res.json())
if __name__ == "__main__":
    predict_sample()
