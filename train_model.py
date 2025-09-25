import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# BASE DIR 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src folder

# DATA nd MODEL PATHS
DATA_PATH = os.path.join(BASE_DIR, "../data/dummy_students.csv")
MODELS_FOLDER = os.path.join(BASE_DIR, "../models")
os.makedirs(MODELS_FOLDER, exist_ok=True)
MODEL_PATH = os.path.join(MODELS_FOLDER, "dropout_model.pkl")

# LOAD DUMMY DATA THROUGH PATH 
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dummy data not found at {DATA_PATH}. Run generate_dummy_data.py first.")

data = pd.read_csv(DATA_PATH)

# TARGET
X = data.drop(columns=['student_id', 'drop_out'])
y = data['drop_out']

categorical_features = ['gender', 'parent_education', 'socioeconomic_status']
numeric_features = ['age', 'attendance_percentage', 'gpa', 'extracurricular_participation', 'previous_failures']

# PREPROCESS
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_features),
    ('cat', OneHotEncoder(), categorical_features)
])

# TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model pipeline
model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
])

# TRAIN MAIN 
model.fit(X_train, y_train)

# EVAL
y_pred = model.predict(X_test)
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# SAVE AND PROCEED
joblib.dump(model, MODEL_PATH)
print(f"\n  Model saved to {MODEL_PATH}")
