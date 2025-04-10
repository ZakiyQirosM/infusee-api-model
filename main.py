import mysql.connector
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd  # Diperlukan untuk membuat DataFrame

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
    id_session: int

@app.post("/prediksi-dari-db")
def prediksi_tpm_dari_db(data: IDInput):
    print("DEBUG: Request diterima dengan data:", data.dict())
    # Fungsi untuk prediksi TPM
    def prediksi_tpm(volume, durasidb, umur):
        input_data = pd.DataFrame([{
            'Volume Infus (ml)': volume,    
            'Durasi': durasidb,
            'Umur': umur
        }])
        tpm = model_tpm.predict(input_data)[0]
        return float(tpm)
    
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            m.berat_total, 
            s.durasi_infus_menit, 
            u.umur
        FROM table_monitoring_infus m
        JOIN infusion_sessions s ON m.id_session = s.id_session
        JOIN table_pasien u ON s.no_reg_pasien = u.no_reg_pasien
        WHERE m.id_session = %s
        ORDER BY m.waktu DESC
        LIMIT 1;
    """
    cursor.execute(query, (data.id_session,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if not result:
        return {"error": "Data tidak ditemukan untuk id_session tersebut"}

    berat_total, durasidb, umur = result

    # Prediksi volume dari berat_total
    volume = model_volume.predict(np.array([[berat_total]]))[0]

    # Prediksi TPM dari volume, durasidb, umur
    tpm = int(round(prediksi_tpm(volume, durasidb, umur)))

    # Simpan ke DB
    conn = get_db_connection()
    cursor = conn.cursor()

    update_query = """
        UPDATE table_monitoring_infus
        SET tpm_prediksi = %s
        WHERE id_session = %s;
    """
    cursor.execute(update_query, (tpm, data.id_session))
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "berat_total": berat_total,
        "durasidb": durasidb,
        "umur": umur,
        "volume_prediksi": int(volume),
        "tpm_prediksi": tpm
    }
