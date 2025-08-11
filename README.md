# 🤖 Infusee-AIOT(ML & API Module)

## 📌 Overview
This repository contains the **Machine Learning** and API module for **Infusee-AIOT**.  
It provides pretrained models and a simple API entry point to serve predictions used by the Infusee website and IoT modules.

**Included artifacts**
- `model_tpm.pkl` — Pretrained model for TPM-related prediction.
- `model_volume.pkl` — Pretrained model for infusion volume prediction.
- `main.py` — API / service entrypoint (check the file for available endpoints and usage).
- `requirements.txt` — Python dependencies.
- `Procfile` — (optional) process file for platform deployments (e.g. Heroku).
  
**Related repositories**
- **Infusee Website (Dashboard)** — https://github.com/ZakiyQirosM/Infusee-IOT
- **Infusee IoT (Device)** — ()

---

## ⚙️ Quickstart

1. **Clone the repository**
```
git clone https://github.com/ZakiyQirosM/infusee-api-model.git
cd infusee-api-model
```

2. **Create and activate a virtual environment (recommended)**
```
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS / Linux
source .venv/bin/activate
```

3. **Install dependencies**
```
pip install -r requirements.txt
```

## Running the API
To avoid conflicts with Laravel (usually running on port 8000), you can specify another port (e.g., 5001).
```
uvicorn main:app --host 0.0.0.0 --port 5001
```
Now the API will be available at:
```
http://localhost:5001
```
---

## 🧠 How to use the pretrained models (Python example)
Here is a safe, generic example to load and use the pickled models:

```python
import pickle
import numpy as np

# Load model
with open("model_volume.pkl", "rb") as f:
    model = pickle.load(f)

# Prepare sample input as numpy array (shape must match training)
# Example placeholder:
X_sample = np.array([[0.1, 0.2, 0.3]])

# Predict
y_pred = model.predict(X_sample)
print("Prediction:", y_pred)
```

> Important: ensure input features and preprocessing match those used at training time. Inspect the repository or training pipeline for required scalers, feature order, or encoders.

---


## 🔍 Notes & Recommendations
- **Security:** Pickled files can execute arbitrary code if tampered with. Only load pickles from trusted sources.
- **Reproducibility:** If you plan to retrain models, include versioned training code and data preprocessing scripts in a separate `training/` folder.
- **API details:** `main.py` likely exposes the HTTP endpoints — open and review it to know expected JSON schema, port, and authentication (if any).
- **Testing:** Add example request samples (cURL, Postman collection) once the endpoints are confirmed.
- Make sure your Laravel backend is configured to communicate with this API at the specified port.
- If running on a server, ensure the chosen port is open in your firewall.

---

## 📜 License & Contact
Include license information or contact details here (add `LICENSE` file if distributing publicly).

---
