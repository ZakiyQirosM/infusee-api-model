import mysql.connector
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

# Load model
model_volume = joblib.load("model_volume.pkl")
model_tpm = joblib.load("model_tpm.pkl")

# Koneksi ke MySQL (XAMPP)
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="mysql_infee"
    )

class IDInput(BaseModel):
    pasien_id: int

@app.post("/prediksi-dari-db")
def prediksi_tpm_dari_db(data: IDInput):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ambil berat_total dari monitoring + durasi dari infusion_sessions
    query = """
        SELECT m.berat_total, s.durasi_infus_menit
        FROM table_monitoring_infus m
        JOIN infusion_sessions s ON m.id_session = s.id_session
        WHERE m.id_session = %s
        ORDER BY m.waktu DESC
        LIMIT 1
    """
    cursor.execute(query, (data.pasien_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if not result:
        return {"error": "Data tidak ditemukan untuk id_session tersebut"}

    berat_total, durasi = result

    # Prediksi volume dari berat total
    volume = model_volume.predict(np.array([[berat_total]]))[0]

    # Prediksi TPM dari volume dan durasi (kalau model butuh dua input)
    tpm = model_tpm.predict(np.array([[volume, durasi]]))[0]

    return {
        "berat_total": berat_total,
        "durasi": durasi,
        "volume_prediksi": int(volume),
        "tpm_prediksi": float(tpm)
    }
