import pickle
from pathlib import Path
from typing import Literal

import pandas as pd
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).resolve().parents[2] / "model" / "model.pkl"
PASS_THRESHOLD = 0.5

with open(MODEL_PATH, "rb") as model_file:
    model_data = pickle.load(model_file)

model = model_data["model"]
encoders = model_data["encoders"]
features = model_data["features"]

router = APIRouter()


class PredictRequest(BaseModel):
    gender: Literal["female", "male"]
    ethnicity: Literal["group A", "group B", "group C", "group D", "group E"]
    parental_education: Literal[
        "some high school",
        "high school",
        "some college",
        "associate's degree",
        "bachelor's degree",
        "master's degree",
    ]
    lunch: Literal["standard", "free/reduced"]
    test_prep: Literal["none", "completed"]
    reading_score: int = Field(ge=0, le=100)
    writing_score: int = Field(ge=0, le=100)


def encode_row(payload: PredictRequest) -> pd.DataFrame:
    row = payload.model_dump()
    encoded = {}
    for col in features:
        if col in encoders:
            encoded[col] = int(encoders[col].transform([row[col]])[0])
        else:
            encoded[col] = row[col]
    return pd.DataFrame([encoded], columns=features)


@router.post("/predict", response_class=PlainTextResponse)
def predict(payload: PredictRequest):
    frame = encode_row(payload)
    class_index = list(model.classes_).index(1)
    probability = float(model.predict_proba(frame)[0][class_index])
    passes = probability > PASS_THRESHOLD
    return "pasa" if passes else "no pasa"
