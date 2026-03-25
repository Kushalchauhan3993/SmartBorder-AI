# 🛡️ SmartBorder AI — Real-Time Intruder Detection & Threat Heatmap System

> GTU Internship 2026 | Problem Domain: Border Defence & Surveillance

---

## 📌 Project Overview

SmartBorder AI is a complete end-to-end machine learning system for real-time border intrusion detection and threat classification. It uses a Random Forest model trained on network intrusion data to detect anomalies, classify severity, and visualize threats on a live tactical dashboard.

---

## 🎯 Features

- ✅ **99.72% accuracy** Random Forest model (best of 4 models tested)
- ✅ **Live Threat Predictor** — input sensor data, get instant prediction
- ✅ **Tactical Heatmap** — geo-visualized threat zones across India border
- ✅ **Real-time MySQL storage** — every prediction auto-saved
- ✅ **Flask REST API** — 5 endpoints for live prediction & stats
- ✅ **Military-themed Streamlit Dashboard** — 5 tabs
- ✅ **Severity Scoring System** — Green / Yellow / Red classification
- ✅ **AI Chatbot** — query threat intelligence conversationally
- ✅ **CSV Export** — download filtered alerts anytime

---

## 🏗️ System Architecture

```
Train_data.csv
      ↓  train.py
Random Forest Model (99.72%)
      ↓  model.pkl + scaler.pkl
Flask REST API  →  localhost:5000
      ↓  POST /predict
MySQL Database  →  smartborder.alerts
      ↓  SELECT *
Streamlit Dashboard  →  localhost:8501
```

---

## 🤖 ML Models Compared

| Model | Accuracy | Selected |
|---|---|---|
| Logistic Regression | 92.14% | ❌ |
| SVM (RBF Kernel) | 97.83% | ❌ |
| Gradient Boosting | 98.45% | ❌ |
| **Random Forest** | **99.72%** | ✅ **WINNER** |

---

## 📊 Dataset

- **Name:** Network Intrusion Detection
- **Source:** Kaggle (sampadab17)
- **Records:** 25,192 rows
- **Features:** 41 input features + 1 target (`class`)
- **Classes:** Normal (13,449) | Anomaly (11,743)

---

## 📐 Severity Scoring System

```
SCORE = model_confidence × 0.5
      + src_bytes  > 1000  → +2
      + serror_rate > 0.3  → +2
      + prediction == 1    → +2
      + dst_bytes  > 1000  → +1

🟢 GREEN  : score < 4.0   → SAFE
🟡 YELLOW : score 4 – 6.5 → MONITOR
🔴 RED    : score ≥ 6.5   → CRITICAL
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/predict` | Run prediction, save to DB |
| GET | `/alerts` | Fetch all alerts |
| GET | `/stats` | Summary statistics |
| GET | `/zones` | Zone-wise breakdown |

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| ML & Training | Python 3.11, Scikit-learn, Pandas, NumPy |
| API | Flask, Flask-CORS |
| Database | MySQL 9.6 |
| Dashboard | Streamlit, Folium, Matplotlib |
| Deployment | Local (Windows + VS Code) |

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install streamlit flask flask-cors scikit-learn pandas numpy mysql-connector-python folium streamlit-folium matplotlib joblib
```

### 2. Setup MySQL
```sql
CREATE DATABASE smartborder;
USE smartborder;
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    src_bytes INT, dst_bytes INT, duration INT,
    serror_rate FLOAT, count_val INT,
    protocol VARCHAR(20), service VARCHAR(50), flag VARCHAR(20),
    prediction INT, severity FLOAT,
    alert_type VARCHAR(10), zone VARCHAR(20)
);
```

### 3. Train the model
```bash
python train.py
```

### 4. Start Flask API (Terminal 1)
```bash
python api.py
```

### 5. Start Streamlit Dashboard (Terminal 2)
```bash
python -m streamlit run app.py
```

### 6. Open browser
- Dashboard: http://localhost:8501
- API: http://localhost:5000

---

## 📁 Project Structure

```
SmartBorder-AI/
├── app.py              ← Streamlit tactical dashboard
├── api.py              ← Flask REST API (port 5000)
├── train.py            ← Train & save ML model
├── requirements.txt    ← All dependencies
├── .gitignore          ← Excludes large/generated files
├── .streamlit/
│   └── config.toml     ← Streamlit dark theme config
└── README.md           ← This file
```

---

## 📸 Dashboard Tabs

| Tab | Description |
|---|---|
| 📊 Intel Overview | KPIs, charts, model comparison, export |
| 🗺️ Tactical Map | Geo heatmap of threat zones |
| 🔮 Live Predictor | Real-time prediction via API |
| 🤖 AI Chatbot | Tactical intelligence assistant |
| 📋 About Project | Dataset, architecture, endpoints |

---

## 👨‍💻 Author

**Kushal** 
> Domain: Border Defence & Surveillance

---

## 📄 License

MIT License — free to use for educational purposes.

