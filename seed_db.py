# seed_db.py — Add sample data to database
import requests
import time

API = "http://localhost:5000/predict"

entries = [
    # GREEN — Normal traffic (5 entries)
    {"src_bytes":180, "dst_bytes":120, "serror_rate":0.0, "count":2,  "duration":1,  "logged_in":1, "root_shell":0, "su_attempted":0, "num_shells":0, "srv_count":2,  "serror_rate":0.0, "srv_serror_rate":0.0, "dst_host_serror_rate":0.0, "dst_host_srv_serror_rate":0.0, "protocol_type":2, "service":3, "flag":1, "dst_host_count":5,  "dst_host_srv_count":5,  "same_srv_rate":1.0, "dst_host_same_srv_rate":1.0, "dst_host_same_src_port_rate":0.5},
    {"src_bytes":240, "dst_bytes":180, "serror_rate":0.0, "count":3,  "duration":2,  "logged_in":1, "root_shell":0, "su_attempted":0, "num_shells":0, "srv_count":3,  "serror_rate":0.0, "srv_serror_rate":0.0, "dst_host_serror_rate":0.0, "dst_host_srv_serror_rate":0.0, "protocol_type":2, "service":3, "flag":1, "dst_host_count":8,  "dst_host_srv_count":8,  "same_srv_rate":1.0, "dst_host_same_srv_rate":1.0, "dst_host_same_src_port_rate":0.5},
    {"src_bytes":300, "dst_bytes":200, "serror_rate":0.0, "count":4,  "duration":0,  "logged_in":1, "root_shell":0, "su_attempted":0, "num_shells":0, "srv_count":4,  "serror_rate":0.0, "srv_serror_rate":0.0, "dst_host_serror_rate":0.0, "dst_host_srv_serror_rate":0.0, "protocol_type":2, "service":2, "flag":1, "dst_host_count":12, "dst_host_srv_count":12, "same_srv_rate":1.0, "dst_host_same_srv_rate":1.0, "dst_host_same_src_port_rate":0.4},
    {"src_bytes":150, "dst_bytes":100, "serror_rate":0.0, "count":1,  "duration":0,  "logged_in":1, "root_shell":0, "su_attempted":0, "num_shells":0, "srv_count":1,  "serror_rate":0.0, "srv_serror_rate":0.0, "dst_host_serror_rate":0.0, "dst_host_srv_serror_rate":0.0, "protocol_type":2, "service":1, "flag":1, "dst_host_count":3,  "dst_host_srv_count":3,  "same_srv_rate":1.0, "dst_host_same_srv_rate":1.0, "dst_host_same_src_port_rate":0.6},
    {"src_bytes":220, "dst_bytes":160, "serror_rate":0.0, "count":2,  "duration":1,  "logged_in":1, "root_shell":0, "su_attempted":0, "num_shells":0, "srv_count":2,  "serror_rate":0.0, "srv_serror_rate":0.0, "dst_host_serror_rate":0.0, "dst_host_srv_serror_rate":0.0, "protocol_type":2, "service":4, "flag":1, "dst_host_count":6,  "dst_host_srv_count":6,  "same_srv_rate":1.0, "dst_host_same_srv_rate":1.0, "dst_host_same_src_port_rate":0.5},

    # YELLOW — Suspicious traffic (3 entries)
    {"src_bytes":3000, "dst_bytes":800,  "serror_rate":0.4, "count":200, "duration":8,  "logged_in":0, "root_shell":0, "su_attempted":0, "num_shells":0, "srv_count":150, "srv_serror_rate":0.4, "dst_host_serror_rate":0.4, "dst_host_srv_serror_rate":0.4, "protocol_type":1, "service":5, "flag":2, "dst_host_count":120, "dst_host_srv_count":100, "same_srv_rate":0.6, "dst_host_same_srv_rate":0.6, "dst_host_same_src_port_rate":0.3},
    {"src_bytes":4000, "dst_bytes":1000, "serror_rate":0.5, "count":250, "duration":10, "logged_in":0, "root_shell":0, "su_attempted":0, "num_shells":1, "srv_count":200, "srv_serror_rate":0.5, "dst_host_serror_rate":0.5, "dst_host_srv_serror_rate":0.5, "protocol_type":1, "service":5, "flag":2, "dst_host_count":150, "dst_host_srv_count":120, "same_srv_rate":0.5, "dst_host_same_srv_rate":0.5, "dst_host_same_src_port_rate":0.4},
    {"src_bytes":2500, "dst_bytes":600,  "serror_rate":0.3, "count":180, "duration":6,  "logged_in":0, "root_shell":0, "su_attempted":0, "num_shells":0, "srv_count":140, "srv_serror_rate":0.3, "dst_host_serror_rate":0.3, "dst_host_srv_serror_rate":0.3, "protocol_type":1, "service":4, "flag":2, "dst_host_count":100, "dst_host_srv_count":90,  "same_srv_rate":0.6, "dst_host_same_srv_rate":0.6, "dst_host_same_src_port_rate":0.3},

    # RED — Critical intrusions (2 entries)
    {"src_bytes":0, "dst_bytes":0, "serror_rate":1.0, "count":511, "duration":0, "logged_in":0, "root_shell":1, "su_attempted":1, "num_shells":2, "srv_count":511, "srv_serror_rate":1.0, "dst_host_serror_rate":1.0, "dst_host_srv_serror_rate":1.0, "protocol_type":1, "service":5, "flag":2, "dst_host_count":255, "dst_host_srv_count":255, "same_srv_rate":1.0, "dst_host_same_srv_rate":1.0, "dst_host_same_src_port_rate":1.0, "num_root":5},
    {"src_bytes":0, "dst_bytes":0, "serror_rate":1.0, "count":511, "duration":0, "logged_in":0, "root_shell":1, "su_attempted":1, "num_shells":3, "srv_count":511, "srv_serror_rate":1.0, "dst_host_serror_rate":1.0, "dst_host_srv_serror_rate":1.0, "protocol_type":1, "service":5, "flag":2, "dst_host_count":255, "dst_host_srv_count":255, "same_srv_rate":1.0, "dst_host_same_srv_rate":1.0, "dst_host_same_src_port_rate":1.0, "num_root":8},
]

print("🔄 Adding entries to database...\n")
for i, entry in enumerate(entries):
    try:
        r = requests.post(API, json=entry, timeout=5)
        result = r.json()
        print(f"✅ Entry {i+1:02d} → {result['alert_emoji']} {result['alert_type']:6} | Severity: {result['severity']} | Zone: {result['zone']}")
        time.sleep(0.3)
    except Exception as e:
        print(f"❌ Entry {i+1} failed: {e}")

print("\n🎉 Done! Check your dashboard and refresh!")
