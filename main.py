from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib

app = FastAPI()
model = joblib.load("model_volume_classifier.pkl")

class BeratInput(BaseModel):
    berat_total: float

@app.post("/klasifikasi-infus")
def klasifikasi_volume(data: BeratInput):
    berat = np.array([[data.berat_total]])
    volume_pred = model.predict(berat)[0]
    return {
        "berat_total": data.berat_total,
        "volume_terklasifikasi": int(volume_pred)
    }
