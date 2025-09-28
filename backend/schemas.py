from pydantic import BaseModel
from typing import Optional, List

class StudentIn(BaseModel):
    student_id: Optional[int]
    age: Optional[int]
    gender: Optional[str]
    attendance_percentage: Optional[float]
    gpa: Optional[float]
    parent_education: Optional[str]
    socioeconomic_status: Optional[str]
    extracurricular_participation: Optional[int]
    previous_failures: Optional[int]
    drop_out: Optional[int] = None

class StudentBatch(BaseModel):
    students: List[StudentIn]

class TrainRequest(BaseModel):
    model_name: Optional[str] = "dropout-model"
    test_size: Optional[float] = 0.2
    max_iter: Optional[int] = 1000

class PredictRequest(BaseModel):
    students: List[StudentIn]
