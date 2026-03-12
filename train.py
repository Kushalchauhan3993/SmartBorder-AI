# train.py — Train ML model and save it to disk
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import mysql.connector

print("🔄 Loading dataset...")
df = pd.read_csv('Train_data.csv')
print(f"✅ Loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# Encode categorical columns
le_protocol = LabelEncoder()
le_service  = LabelEncoder()
le_flag     = LabelEncoder()

df['protocol_type'] = le_protocol.fit_transform(df['protocol_type'])
df['service']       = le_service.fit_transform(df['service'])
df['flag']          = le_flag.fit_transform(df['flag'])
df['class']         = df['class'].map({'normal': 0, 'anomaly': 1})

X = df.drop('class', axis=1)
y = df['class']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

scaler     = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

print("🤖 Training Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train_sc, y_train)

preds = model.predict(X_test_sc)
acc   = accuracy_score(y_test, preds) * 100
print(f"✅ Accuracy: {acc:.2f}%")
print(classification_report(y_test, preds, target_names=['Normal','Anomaly']))

# Save everything
joblib.dump(model,            'model.pkl')
joblib.dump(scaler,           'scaler.pkl')
joblib.dump(list(X.columns),  'feature_names.pkl')
joblib.dump(le_protocol,      'le_protocol.pkl')
joblib.dump(le_service,       'le_service.pkl')
joblib.dump(le_flag,          'le_flag.pkl')
print("✅ model.pkl, scaler.pkl, feature_names.pkl saved!")

# Save accuracy to MySQL
try:
    conn   = mysql.connector.connect(
        host='localhost', user='root',
        password='root1234', database='smartborder'
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO model_stats (model_name, accuracy) VALUES (%s, %s)",
        ('Random Forest', round(acc, 2))
    )
    conn.commit()
    conn.close()
    print("✅ Model accuracy saved to MySQL database!")
except Exception as e:
    print(f"⚠️  MySQL error (training still succeeded): {e}")

print("\n🎉 Training complete! Ready to run api.py")
