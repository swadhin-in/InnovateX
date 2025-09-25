import pandas as pd
import numpy as np
import os

def generate_dummy_data(num_students: int = 2000 , seed: int = 42):
    np.random.seed(seed)

    data = pd.DataFrame({
        'student_id': range(1, num_students+1),
        'age': np.random.randint(16, 23, num_students),
        'gender': np.random.choice(['Male', 'Female'], num_students),
        'attendance_percentage': np.random.uniform(50, 100, num_students),
        'gpa': np.random.uniform(0, 10, num_students),
        'parent_education': np.random.choice(['High School', 'Graduate', 'Postgraduate'], num_students),
        'socioeconomic_status': np.random.choice(['Low', 'Medium', 'High'], num_students),
        'extracurricular_participation': np.random.randint(0, 6, num_students),
        'previous_failures': np.random.randint(0, 4, num_students)
    })

    # SIM
    risk_score = (
        (100 - data['attendance_percentage']) * 0.4 +
        (10 - data['gpa']) * 0.3 +
        data['previous_failures'] * 10 +
        data['socioeconomic_status'].map({'Low': 10, 'Medium': 5, 'High': 0}) +
        np.random.normal(0, 5, num_students)
    )

    threshold = np.percentile(risk_score, 85)  # Top 15% risky
    data['drop_out'] = (risk_score >= threshold).astype(int)

    return data

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src folder
    DATA_FOLDER = os.path.join(BASE_DIR, "../data")
    os.makedirs(DATA_FOLDER, exist_ok=True)  # create folder if it doesn't exist

    OUTPUT_PATH = os.path.join(DATA_FOLDER, "dummy_students.csv")

    df = generate_dummy_data()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f" Dummy data saved to {OUTPUT_PATH}")
