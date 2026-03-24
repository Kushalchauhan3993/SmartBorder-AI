# bulk_add.py — SmartBorder AI | One-time 4500 entry bulk seeder
import mysql.connector
import random
from datetime import datetime, timedelta

DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'root1234',
    'database': 'smartborder'
}

PROTOCOLS = [0, 1, 2]  # 0=icmp, 1=tcp, 2=udp
SERVICES  = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # encoded service values
FLAGS     = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # encoded flag values
ZONES     = ['North', 'West', 'East', 'South']
ZONE_W    = [0.35, 0.30, 0.20, 0.15]

def random_entry(alert_type, days_ago):
    zone = random.choices(ZONES, weights=ZONE_W)[0]

    # Timestamp — spread over past 25 days
    base = datetime.now() - timedelta(days=days_ago)
    secs = random.randint(0, 86400)
    ts   = base + timedelta(seconds=secs)

    if alert_type == 'Green':
        src_bytes   = random.randint(0, 900)
        dst_bytes   = random.randint(0, 600)
        duration    = random.randint(0, 15)
        serror_rate = round(random.uniform(0.0, 0.1), 2)
        count       = random.randint(1, 60)
        prediction  = 0
        proba       = round(random.uniform(0.05, 0.35), 3)
        severity    = round(min(proba * 5 + random.uniform(0, 1.5), 3.9), 2)

    elif alert_type == 'Yellow':
        src_bytes   = random.randint(500, 6000)
        dst_bytes   = random.randint(200, 2500)
        duration    = random.randint(0, 45)
        serror_rate = round(random.uniform(0.1, 0.4), 2)
        count       = random.randint(20, 220)
        prediction  = random.choice([0, 0, 1])
        proba       = round(random.uniform(0.35, 0.65), 3)
        severity    = round(max(4.0, min(proba * 5 + random.uniform(1.5, 3.0), 6.4)), 2)

    else:  # Red
        src_bytes   = random.randint(1500, 35000)
        dst_bytes   = random.randint(500, 9000)
        duration    = random.randint(0, 90)
        serror_rate = round(random.uniform(0.3, 1.0), 2)
        count       = random.randint(100, 511)
        prediction  = 1
        proba       = round(random.uniform(0.65, 0.99), 3)
        severity    = round(max(6.5, min(proba * 5 + random.uniform(2.0, 4.5), 10.0)), 2)

    return {
        'timestamp':   ts.strftime('%Y-%m-%d %H:%M:%S'),
        'src_bytes':   src_bytes,
        'dst_bytes':   dst_bytes,
        'duration':    duration,
        'serror_rate': serror_rate,
        'count_val':   count,
        'protocol':    random.choice(PROTOCOLS),
        'service':     random.choice(SERVICES),
        'flag':        random.choice(FLAGS),
        'prediction':  prediction,
        'severity':    severity,
        'alert_type':  alert_type,
        'zone':        zone,
    }

def get_total(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM alerts")
    t = cur.fetchone()[0]
    cur.close()
    return t

def main():
    TOTAL     = 8000
    N_GREEN   = int(TOTAL * 0.45)   # 2025
    N_YELLOW  = int(TOTAL * 0.32)   # 1440
    N_RED     = TOTAL - N_GREEN - N_YELLOW  # 1035

    print("=" * 50)
    print("SmartBorder AI — Bulk Entry Generator")
    print(f"Generating {TOTAL:,} entries...")
    print(f"  Green  : {N_GREEN:,}")
    print(f"  Yellow : {N_YELLOW:,}")
    print(f"  Red    : {N_RED:,}")
    print("=" * 50)

    entries = []
    # Spread timestamps over past 25 days
    for i in range(N_GREEN):
        entries.append(random_entry('Green',  random.randint(0, 25)))
    for i in range(N_YELLOW):
        entries.append(random_entry('Yellow', random.randint(0, 25)))
    for i in range(N_RED):
        entries.append(random_entry('Red',    random.randint(0, 25)))

    random.shuffle(entries)

    conn = mysql.connector.connect(**DB_CONFIG)
    before = get_total(conn)
    print(f"DB before : {before:,} records")

    cur = conn.cursor()
    sql = """
        INSERT INTO alerts
            (timestamp, src_bytes, dst_bytes, duration, serror_rate,
             count_val, protocol, service, flag, prediction,
             severity, alert_type, zone)
        VALUES
            (%(timestamp)s, %(src_bytes)s, %(dst_bytes)s, %(duration)s,
             %(serror_rate)s, %(count_val)s, %(protocol)s, %(service)s,
             %(flag)s, %(prediction)s, %(severity)s, %(alert_type)s, %(zone)s)
    """

    # Insert in batches of 500
    batch_size = 500
    inserted   = 0
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i+batch_size]
        cur.executemany(sql, batch)
        conn.commit()
        inserted += len(batch)
        print(f"  Inserted {inserted:,} / {TOTAL:,}...")

    after = get_total(conn)
    cur.close()
    conn.close()

    print("=" * 50)
    print(f"Done!")
    print(f"DB before : {before:,}")
    print(f"DB after  : {after:,}")
    print(f"Added     : {after - before:,} entries")
    print("Refresh your Streamlit dashboard to see updated numbers!")
    print("=" * 50)

if __name__ == '__main__':
    main()
