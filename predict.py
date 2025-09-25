import pandas as pd
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src folder
MODEL_PATH = os.path.join(BASE_DIR, "../models/dropout_model.pkl")
INPUT_CSV = os.path.join(BASE_DIR, "../data/new_students.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "../data/predicted_students.csv")

# LIOAD
model = joblib.load(MODEL_PATH)

# LAOD INOUT SET
new_students = pd.read_csv(INPUT_CSV)

# PREDICT
predictions = model.predict(new_students)
probabilities = model.predict_proba(new_students)[:, 1]

# ADD
new_students['Prediction'] = ["Dropout" if p == 1 else "Not Dropout" for p in predictions]
new_students['Dropout Probability (%)'] = (probabilities * 100).round(2)

print(new_students)

# SAVE AND PROCEED
new_students.to_csv(OUTPUT_CSV, index=False)
print(f"\n  Predictions saved to {OUTPUT_CSV}")

