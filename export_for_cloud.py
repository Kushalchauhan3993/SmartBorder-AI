import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root1234',
    database='smartborder'
)
df = pd.read_sql("SELECT * FROM alerts ORDER BY timestamp DESC", conn)
conn.close()
df.to_csv('border_alerts.csv', index=False)
print(f"Done! Exported {len(df):,} records to border_alerts.csv")