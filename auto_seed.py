# auto_seed.py — SmartBorder AI | Daily Auto Entry Generator
# Adds 100-200 realistic entries to MySQL every time it runs
# Schedule via Windows Task Scheduler to run daily automatically

import mysql.connector
import random
import json
import os
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'root1234',
    'database': 'smartborder'
}

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auto_seed_log.txt')

# ── Auto Stop Date ────────────────────────────────────
STOP_DATE = datetime(2026, 4, 10)   # ← change this to your submission date
if datetime.now() > STOP_DATE:
    print("Auto seeder expired. Submission date passed.")
    exit()
    
# ── Realistic Data Pools ──────────────────────────────
PROTOCOLS = ['tcp', 'udp', 'icmp']
SERVICES  = ['http', 'ftp', 'smtp', 'ssh', 'dns', 'telnet', 'finger', 'pop3', 'imap4', 'domain']
FLAGS     = ['SF', 'S0', 'REJ', 'RSTO', 'SH', 'OTH', 'S1', 'S2', 'S3', 'RSTOS0']
ZONES     = ['North', 'West', 'East', 'South']

# Weighted zone distribution — North and West more active (border zones)
ZONE_WEIGHTS = [0.35, 0.30, 0.20, 0.15]

def random_entry(target_type=None):
    """Generate one realistic alert entry."""

    # Distribution: 45% Green, 32% Yellow, 23% Red
    if target_type is None:
        roll = random.random()
        if roll < 0.45:
            target_type = 'Green'
        elif roll < 0.77:
            target_type = 'Yellow'
        else:
            target_type = 'Red'

    zone = random.choices(ZONES, weights=ZONE_WEIGHTS)[0]

    if target_type == 'Green':
        src_bytes    = random.randint(0, 800)
        dst_bytes    = random.randint(0, 500)
        duration     = random.randint(0, 10)
        serror_rate  = round(random.uniform(0.0, 0.1), 2)
        count        = random.randint(1, 50)
        prediction   = 0
        proba        = round(random.uniform(0.05, 0.35), 3)
        severity     = round(proba * 5 + random.uniform(0, 1.5), 2)
        severity     = min(severity, 3.9)

    elif target_type == 'Yellow':
        src_bytes    = random.randint(500, 5000)
        dst_bytes    = random.randint(200, 2000)
        duration     = random.randint(0, 40)
        serror_rate  = round(random.uniform(0.1, 0.4), 2)
        count        = random.randint(20, 200)
        prediction   = random.choice([0, 0, 1])
        proba        = round(random.uniform(0.35, 0.65), 3)
        severity     = round(proba * 5 + random.uniform(1.5, 3.0), 2)
        severity     = max(4.0, min(severity, 6.4))

    else:  # Red
        src_bytes    = random.randint(1500, 30000)
        dst_bytes    = random.randint(500, 8000)
        duration     = random.randint(0, 80)
        serror_rate  = round(random.uniform(0.3, 1.0), 2)
        count        = random.randint(100, 511)
        prediction   = 1
        proba        = round(random.uniform(0.65, 0.99), 3)
        severity     = round(proba * 5 + random.uniform(2.0, 4.5), 2)
        severity     = max(6.5, min(severity, 10.0))

    # Slightly randomize timestamp within today
    now   = datetime.now()
    start = now.replace(hour=0, minute=0, second=0)
    end   = now
    secs  = random.randint(0, int((end - start).total_seconds()))
    ts    = start + timedelta(seconds=secs)

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
        'alert_type':  target_type,
        'zone':        zone,
    }

def insert_entries(entries):
    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()
    sql  = """
        INSERT INTO alerts
            (timestamp, src_bytes, dst_bytes, duration, serror_rate,
             count_val, protocol, service, flag, prediction,
             severity, alert_type, zone)
        VALUES
            (%(timestamp)s, %(src_bytes)s, %(dst_bytes)s, %(duration)s,
             %(serror_rate)s, %(count_val)s, %(protocol)s, %(service)s,
             %(flag)s, %(prediction)s, %(severity)s, %(alert_type)s, %(zone)s)
    """
    cur.executemany(sql, entries)
    conn.commit()
    inserted = cur.rowcount
    cur.close()
    conn.close()
    return inserted

def get_total():
    conn  = mysql.connector.connect(**DB_CONFIG)
    cur   = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM alerts")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def main():
    log("=" * 55)
    log("SmartBorder AI — Daily Auto Seeder STARTED")

    # Random count between 130 and 180 entries today
    count = random.randint(130, 180)

    # Realistic daily distribution
    n_green  = int(count * 0.45)
    n_yellow = int(count * 0.32)
    n_red    = count - n_green - n_yellow

    entries = []
    entries += [random_entry('Green')  for _ in range(n_green)]
    entries += [random_entry('Yellow') for _ in range(n_yellow)]
    entries += [random_entry('Red')    for _ in range(n_red)]

    random.shuffle(entries)

    try:
        inserted = insert_entries(entries)
        total    = get_total()
        log(f"Inserted  : {inserted} entries")
        log(f"  Green   : {n_green}")
        log(f"  Yellow  : {n_yellow}")
        log(f"  Red     : {n_red}")
        log(f"Total DB  : {total:,} records")
        log("Status    : SUCCESS")
    except Exception as e:
        log(f"ERROR     : {e}")

    log("=" * 55)

if __name__ == '__main__':
    main()
