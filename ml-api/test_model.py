import pickle
from pathlib import Path

import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / "model" / "model.pkl"
PASS_THRESHOLD = 0.5

sample = {
    "gender": "female",
    "ethnicity": "group A",
    "parental_education": "some high school",
    "lunch": "free/reduced",
    "test_prep": "none",
    "reading_score": 72,
    "writing_score": 70,
}

# Categorías válidas:
# gender: female, male
# ethnicity: group A, group B, group C, group D, group E
# parental_education: some high school, high school, some college, associate's degree, bachelor's degree, master's degree
# lunch: standard, free/reduced
# test_prep: none, completed
# reading_score y writing_score: enteros de 0 a 100

with open(MODEL_PATH, "rb") as model_file:
    model_data = pickle.load(model_file)

model = model_data["model"]
encoders = model_data["encoders"]
features = model_data["features"]

encoded = {}
for col in features:
    if col in encoders:
        encoded[col] = int(encoders[col].transform([sample[col]])[0])
    else:
        encoded[col] = sample[col]

frame = pd.DataFrame([encoded], columns=features)
class_index = list(model.classes_).index(1)
probability = float(model.predict_proba(frame)[0][class_index])
passes = probability > PASS_THRESHOLD

print("pasa" if passes else "no pasa")
