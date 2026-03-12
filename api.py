# api.py — Flask REST API for SmartBorder AI
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import mysql.connector
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# Load saved model files
print("🔄 Loading model files...")
model         = joblib.load('model.pkl')
scaler        = joblib.load('scaler.pkl')
feature_names = joblib.load('feature_names.pkl')
print("✅ Model loaded successfully!")

ZONES = ['North', 'South', 'East', 'West']

def get_db():
    return mysql.connector.connect(
        host='localhost', user='root',
        password='root1234', database='smartborder'
    )

def calculate_severity(proba, src_bytes, serror_rate, prediction, dst_bytes):
    score  = proba * 5
    score += 2 if src_bytes   > 1000 else (1 if src_bytes   > 500 else 0)
    score += 2 if serror_rate > 0.3  else (1 if serror_rate > 0.1 else 0)
    score += 2 if prediction == 1    else 0
    score += 1 if dst_bytes   > 1000 else 0
    return round(min(score, 10), 1)

# ── ROUTE 1: Health Check ─────────────────────────────
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status":   "✅ SmartBorder AI API is running!",
        "accuracy": "99.72%",
        "version":  "1.0",
        "routes": {
            "GET  /":           "Health check",
            "POST /predict":    "Predict threat from sensor data",
            "GET  /alerts":     "Get all saved alerts from database",
            "GET  /stats":      "Get summary statistics",
            "GET  /zones":      "Get zone-wise risk summary"
        }
    })

# ── ROUTE 2: Predict ──────────────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Build feature vector
        features    = [float(data.get(f, 0)) for f in feature_names]
        features_sc = scaler.transform([features])

        prediction  = int(model.predict(features_sc)[0])
        proba       = float(model.predict_proba(features_sc)[0][1])

        src_bytes   = float(data.get('src_bytes',   0))
        dst_bytes   = float(data.get('dst_bytes',   0))
        serror_rate = float(data.get('serror_rate', 0))
        duration    = float(data.get('duration',    0))
        count       = float(data.get('count',       0))
        protocol    = int(data.get('protocol_type', 0))
        service     = int(data.get('service',       0))
        flag        = int(data.get('flag',          0))

        severity   = calculate_severity(
            proba, src_bytes, serror_rate, prediction, dst_bytes)
        alert_type = 'Red'    if severity >= 6.5 else \
                     'Yellow' if severity >= 4   else 'Green'
        zone       = random.choice(ZONES)

        # Save to MySQL
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts
            (src_bytes, dst_bytes, duration, serror_rate,
             count_val, protocol, service, flag,
             prediction, severity, alert_type, zone)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (src_bytes, dst_bytes, duration, serror_rate,
              count, protocol, service, flag,
              prediction, severity, alert_type, zone))
        conn.commit()
        alert_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "alert_id":    alert_id,
            "prediction":  prediction,
            "label":       "🚨 INTRUSION" if prediction == 1 else "✅ Normal",
            "probability": round(proba * 100, 2),
            "severity":    severity,
            "alert_type":  alert_type,
            "alert_emoji": "🔴" if alert_type == "Red" else
                           "🟡" if alert_type == "Yellow" else "🟢",
            "zone":        zone,
            "action":      "Immediate response required!" if alert_type == "Red" else
                           "Monitor closely"              if alert_type == "Yellow" else
                           "No action needed",
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── ROUTE 3: Get All Alerts ───────────────────────────
@app.route('/alerts', methods=['GET'])
def get_alerts():
    try:
        limit      = int(request.args.get('limit', 50))
        alert_type = request.args.get('type', None)
        zone       = request.args.get('zone', None)

        conn   = get_db()
        cursor = conn.cursor(dictionary=True)

        query  = "SELECT * FROM alerts WHERE 1=1"
        params = []
        if alert_type:
            query += " AND alert_type = %s"
            params.append(alert_type)
        if zone:
            query += " AND zone = %s"
            params.append(zone)
        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        alerts = cursor.fetchall()
        conn.close()

        for a in alerts:
            a['timestamp'] = str(a['timestamp'])

        return jsonify({
            "total":  len(alerts),
            "alerts": alerts
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── ROUTE 4: Stats ────────────────────────────────────
@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as total FROM alerts")
        total = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as c FROM alerts WHERE alert_type='Red'")
        red = cursor.fetchone()['c']

        cursor.execute("SELECT COUNT(*) as c FROM alerts WHERE alert_type='Yellow'")
        yellow = cursor.fetchone()['c']

        cursor.execute("SELECT COUNT(*) as c FROM alerts WHERE alert_type='Green'")
        green = cursor.fetchone()['c']

        cursor.execute("SELECT AVG(severity) as avg_sev FROM alerts")
        avg_sev = cursor.fetchone()['avg_sev'] or 0

        cursor.execute("SELECT COUNT(*) as c FROM alerts WHERE prediction=1")
        intrusions = cursor.fetchone()['c']

        cursor.execute(
            "SELECT accuracy FROM model_stats ORDER BY id DESC LIMIT 1")
        row      = cursor.fetchone()
        accuracy = row['accuracy'] if row else 99.72
        conn.close()

        return jsonify({
            "total_alerts":     total,
            "red_alerts":       red,
            "yellow_alerts":    yellow,
            "green_alerts":     green,
            "intrusions":       intrusions,
            "avg_severity":     round(float(avg_sev), 2),
            "model_accuracy":   f"{accuracy}%",
            "false_alarm_rate": f"{round((green/max(total,1))*100,1)}%"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── ROUTE 5: Zones ────────────────────────────────────
@app.route('/zones', methods=['GET'])
def get_zones():
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                zone,
                COUNT(*)         AS total_alerts,
                SUM(prediction)  AS intrusions,
                AVG(severity)    AS avg_severity,
                SUM(CASE WHEN alert_type='Red'    THEN 1 ELSE 0 END) AS red,
                SUM(CASE WHEN alert_type='Yellow' THEN 1 ELSE 0 END) AS yellow,
                SUM(CASE WHEN alert_type='Green'  THEN 1 ELSE 0 END) AS green
            FROM alerts
            GROUP BY zone
            ORDER BY avg_severity DESC
        """)
        zones = cursor.fetchall()
        conn.close()

        for z in zones:
            z['avg_severity'] = round(float(z['avg_severity'] or 0), 2)
            z['risk_level']   = "🔴 High"   if z['avg_severity'] >= 7 else \
                                "🟡 Medium" if z['avg_severity'] >= 4 else \
                                "🟢 Low"

        return jsonify({
            "total_zones": len(zones),
            "zones":       zones
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  🛡️  SmartBorder AI — REST API")
    print("="*50)
    print("📡 Running at : http://localhost:5000")
    print("📋 Endpoints  :")
    print("   GET  /         — Health check")
    print("   POST /predict  — Predict threat")
    print("   GET  /alerts   — View all alerts")
    print("   GET  /stats    — Summary stats")
    print("   GET  /zones    — Zone risk summary")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
