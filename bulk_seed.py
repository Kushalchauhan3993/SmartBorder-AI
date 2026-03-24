# bulk_seed.py — Add 2500 realistic entries to database
import requests
import random
import time

API = "http://localhost:5000/predict"

def make_green():
    return {
        "duration":         random.randint(0, 5),
        "protocol_type":    random.randint(1, 3),
        "service":          random.randint(1, 10),
        "flag":             1,
        "src_bytes":        random.randint(50, 500),
        "dst_bytes":        random.randint(20, 300),
        "land":             0,
        "wrong_fragment":   0,
        "urgent":           0,
        "hot":              0,
        "num_failed_logins":0,
        "logged_in":        1,
        "num_compromised":  0,
        "root_shell":       0,
        "su_attempted":     0,
        "num_root":         0,
        "num_file_creations":0,
        "num_shells":       0,
        "num_access_files": 0,
        "num_outbound_cmds":0,
        "is_host_login":    0,
        "is_guest_login":   0,
        "count":            random.randint(1, 20),
        "srv_count":        random.randint(1, 20),
        "serror_rate":      round(random.uniform(0.0, 0.05), 2),
        "srv_serror_rate":  round(random.uniform(0.0, 0.05), 2),
        "rerror_rate":      0.0,
        "srv_rerror_rate":  0.0,
        "same_srv_rate":    round(random.uniform(0.8, 1.0), 2),
        "diff_srv_rate":    round(random.uniform(0.0, 0.1), 2),
        "srv_diff_host_rate":0.0,
        "dst_host_count":   random.randint(1, 30),
        "dst_host_srv_count":random.randint(1, 30),
        "dst_host_same_srv_rate":    round(random.uniform(0.7, 1.0), 2),
        "dst_host_diff_srv_rate":    round(random.uniform(0.0, 0.1), 2),
        "dst_host_same_src_port_rate":round(random.uniform(0.3, 0.8), 2),
        "dst_host_srv_diff_host_rate":0.0,
        "dst_host_serror_rate":      0.0,
        "dst_host_srv_serror_rate":  0.0,
        "dst_host_rerror_rate":      0.0,
        "dst_host_srv_rerror_rate":  0.0,
    }

def make_yellow():
    return {
        "duration":         random.randint(3, 15),
        "protocol_type":    random.randint(1, 2),
        "service":          random.randint(3, 8),
        "flag":             2,
        "src_bytes":        random.randint(1000, 6000),
        "dst_bytes":        random.randint(300, 2000),
        "land":             0,
        "wrong_fragment":   random.randint(0, 2),
        "urgent":           0,
        "hot":              random.randint(1, 5),
        "num_failed_logins":random.randint(0, 2),
        "logged_in":        0,
        "num_compromised":  random.randint(0, 3),
        "root_shell":       0,
        "su_attempted":     0,
        "num_root":         0,
        "num_file_creations":0,
        "num_shells":       random.randint(0, 1),
        "num_access_files": random.randint(0, 2),
        "num_outbound_cmds":0,
        "is_host_login":    0,
        "is_guest_login":   random.randint(0, 1),
        "count":            random.randint(100, 300),
        "srv_count":        random.randint(80, 250),
        "serror_rate":      round(random.uniform(0.2, 0.6), 2),
        "srv_serror_rate":  round(random.uniform(0.2, 0.6), 2),
        "rerror_rate":      round(random.uniform(0.0, 0.2), 2),
        "srv_rerror_rate":  round(random.uniform(0.0, 0.2), 2),
        "same_srv_rate":    round(random.uniform(0.3, 0.7), 2),
        "diff_srv_rate":    round(random.uniform(0.1, 0.3), 2),
        "srv_diff_host_rate":round(random.uniform(0.0, 0.2), 2),
        "dst_host_count":   random.randint(80, 180),
        "dst_host_srv_count":random.randint(60, 150),
        "dst_host_same_srv_rate":    round(random.uniform(0.3, 0.7), 2),
        "dst_host_diff_srv_rate":    round(random.uniform(0.1, 0.3), 2),
        "dst_host_same_src_port_rate":round(random.uniform(0.2, 0.5), 2),
        "dst_host_srv_diff_host_rate":round(random.uniform(0.0, 0.2), 2),
        "dst_host_serror_rate":      round(random.uniform(0.2, 0.6), 2),
        "dst_host_srv_serror_rate":  round(random.uniform(0.2, 0.6), 2),
        "dst_host_rerror_rate":      round(random.uniform(0.0, 0.2), 2),
        "dst_host_srv_rerror_rate":  round(random.uniform(0.0, 0.2), 2),
    }

def make_red():
    return {
        "duration":         0,
        "protocol_type":    1,
        "service":          random.randint(4, 8),
        "flag":             2,
        "src_bytes":        random.randint(0, 100),
        "dst_bytes":        0,
        "land":             0,
        "wrong_fragment":   0,
        "urgent":           0,
        "hot":              random.randint(0, 5),
        "num_failed_logins":0,
        "logged_in":        0,
        "num_compromised":  random.randint(0, 5),
        "root_shell":       random.randint(0, 1),
        "su_attempted":     random.randint(0, 1),
        "num_root":         random.randint(0, 10),
        "num_file_creations":0,
        "num_shells":       random.randint(1, 4),
        "num_access_files": 0,
        "num_outbound_cmds":0,
        "is_host_login":    0,
        "is_guest_login":   0,
        "count":            random.randint(400, 511),
        "srv_count":        random.randint(400, 511),
        "serror_rate":      round(random.uniform(0.8, 1.0), 2),
        "srv_serror_rate":  round(random.uniform(0.8, 1.0), 2),
        "rerror_rate":      0.0,
        "srv_rerror_rate":  0.0,
        "same_srv_rate":    round(random.uniform(0.8, 1.0), 2),
        "diff_srv_rate":    0.0,
        "srv_diff_host_rate":0.0,
        "dst_host_count":   random.randint(200, 255),
        "dst_host_srv_count":random.randint(200, 255),
        "dst_host_same_srv_rate":    round(random.uniform(0.8, 1.0), 2),
        "dst_host_diff_srv_rate":    0.0,
        "dst_host_same_src_port_rate":round(random.uniform(0.8, 1.0), 2),
        "dst_host_srv_diff_host_rate":0.0,
        "dst_host_serror_rate":      round(random.uniform(0.8, 1.0), 2),
        "dst_host_srv_serror_rate":  round(random.uniform(0.8, 1.0), 2),
        "dst_host_rerror_rate":      0.0,
        "dst_host_srv_rerror_rate":  0.0,
    }

# ── Distribution ──────────────────────────────────────
# 2500 total: 1200 Green, 800 Yellow, 500 Red
entries = (
    [('Green',  make_green)  for _ in range(1200)] +
    [('Yellow', make_yellow) for _ in range(800)]  +
    [('Red',    make_red)    for _ in range(500)]
)
random.shuffle(entries)

# ── Run ───────────────────────────────────────────────
print("="*55)
print("  🛡️  SmartBorder AI — Bulk Database Seeder")
print("  Adding 2,500 entries (Green/Yellow/Red mix)")
print("="*55)

success = 0
failed  = 0
green_c = yellow_c = red_c = 0

for i, (expected, fn) in enumerate(entries):
    try:
        r      = requests.post(API, json=fn(), timeout=5)
        result = r.json()
        alert  = result.get('alert_type','?')

        if alert == 'Green':  green_c  += 1
        if alert == 'Yellow': yellow_c += 1
        if alert == 'Red':    red_c    += 1
        success += 1

        # Progress every 100 entries
        if (i+1) % 100 == 0:
            print(f"  ✅ {i+1:4d}/2500 | 🟢 {green_c} | 🟡 {yellow_c} | 🔴 {red_c}")

    except Exception as e:
        failed += 1
        if failed <= 3:
            print(f"  ❌ Entry {i+1} failed: {e}")

print("\n" + "="*55)
print(f"  🎉 COMPLETE!")
print(f"  ✅ Success : {success:,}")
print(f"  ❌ Failed  : {failed}")
print(f"  🟢 Green   : {green_c:,}")
print(f"  🟡 Yellow  : {yellow_c:,}")
print(f"  🔴 Red     : {red_c:,}")
print(f"  📊 Total   : {success:,} entries in database")
print("="*55)
print("\n  Refresh your Streamlit dashboard to see the data!")
