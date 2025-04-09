from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib

app = FastAPI()

# Load kedua model
model_volume = joblib.load("model_volume.pkl")
model_tpm = joblib.load("model_tpm.pkl")

# Schema untuk input
class BeratInput(BaseModel):
    berat_total: float

@app.post("/klasifikasi-volume")
def klasifikasi_volume(data: BeratInput):
    berat = np.array([[data.berat_total]])
    volume_pred = model_volume.predict(berat)[0]
    return {
        "volume": int(volume_pred)
    }

@app.post("/prediksi-tpm")
def prediksi_tpm(data: BeratInput):
    berat = np.array([[data.berat_total]])
    tpm_pred = model_tpm.predict(berat)[0]
    return {
        "tpm_prediksi": float(tpm_pred)
    }
