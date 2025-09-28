from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, unique=True, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    attendance_percentage = Column(Float, nullable=True)
    gpa = Column(Float, nullable=True)
    parent_education = Column(String, nullable=True)
    socioeconomic_status = Column(String, nullable=True)
    extracurricular_participation = Column(Integer, nullable=True)
    previous_failures = Column(Integer, nullable=True)
    drop_out = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ModelArtifact(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata_json = Column("metadata", JSON, nullable=True)

class TrainingRun(Base):
    __tablename__ = "training_runs"
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    params = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    model = relationship("ModelArtifact")

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    raw_student_id = Column(Integer, nullable=True)
    predicted_label = Column(Integer, nullable=False)
    probability = Column(Float, nullable=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    student = relationship("Student")
    model = relationship("ModelArtifact")
