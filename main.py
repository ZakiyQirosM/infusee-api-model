import mysql.connector
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

# Load model
model_volume = joblib.load("model_volume.pkl")
model_tpm = joblib.load("model_tpm.pkl")

min_berat_total = 100
max_berat_total = 2000

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

    # Ambil data dari database
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    m.berat_total, 
                    s.durasi_infus_jam, 
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

    if not result:
        return {"error": "Data tidak ditemukan untuk id_session tersebut"}

    berat_total, durasidb, umur = result

    if berat_total < min_berat_total or berat_total > max_berat_total:
        return {"error": f"Berat total {berat_total} di luar jangkauan training data"}
    
    # Prediksi volume dari berat_total
    input_volume_df = pd.DataFrame([{
    "Berat Total (g)": berat_total
    }])
    volume = model_volume.predict(input_volume_df)[0]

    # Prediksi TPM
    input_tpm_df = pd.DataFrame([{
        'Volume Infus (ml)': volume,
        'Durasi': durasidb,
        'Umur': umur
    }])
    tpm = int(round(model_tpm.predict(input_tpm_df)[0]))

    # Update TPM ke database
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            update_query = """
                UPDATE table_monitoring_infus
                SET tpm_prediksi = %s
                WHERE id_session = %s;
            """
            cursor.execute(update_query, (tpm, data.id_session))
            conn.commit()

    return {
        "berat_total": berat_total,
        "durasidb": durasidb,
        "umur": umur,
        "volume_prediksi": int(volume),
        "tpm_prediksi": tpm
    }
