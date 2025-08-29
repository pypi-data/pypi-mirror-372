import requests, time

BASE = "http://127.0.0.1:8050"

# Same datasets each time; only statuses/values change
SNAP_A = [
    # LIVE / prices
    {"run_type":"live","data_name":"prices","stage":"stage",   "counts":{"wait":5}},
    {"run_type":"live","data_name":"prices","stage":"archive", "counts":{"wait":2}},
    {"run_type":"live","data_name":"prices","stage":"enrich",  "counts":{"running":3}},

    # LIVE / alpha
    {"run_type":"live","data_name":"alpha","stage":"stage",   "counts":{"overdue":2}},
    {"run_type":"live","data_name":"alpha","stage":"archive", "counts":{"wait":1}},
    {"run_type":"live","data_name":"alpha","stage":"enrich",  "counts":{"wait":1}},

    # BACKFILL / alpha
    {"run_type":"backfill","data_name":"alpha","stage":"stage",   "counts":{"retry":2}},
    {"run_type":"backfill","data_name":"alpha","stage":"archive", "counts":{"wait":3}},
    {"run_type":"backfill","data_name":"alpha","stage":"enrich",  "counts":{"failed":1}},
]

SNAP_B = [
    # prices moves to succeeded
    {"run_type":"live","data_name":"prices","stage":"stage",   "counts":{"succeeded":5}},
    {"run_type":"live","data_name":"prices","stage":"archive", "counts":{"succeeded":2}},
    {"run_type":"live","data_name":"prices","stage":"enrich",  "counts":{"succeeded":3}},

    # alpha overdue cleared, now running
    {"run_type":"live","data_name":"alpha","stage":"stage",   "counts":{"running":2}},
    {"run_type":"live","data_name":"alpha","stage":"archive", "counts":{"succeeded":1}},
    {"run_type":"live","data_name":"alpha","stage":"enrich",  "counts":{"wait":1}},

    # backfill alpha retry resolved, now succeeded
    {"run_type":"backfill","data_name":"alpha","stage":"stage",   "counts":{"succeeded":2}},
    {"run_type":"backfill","data_name":"alpha","stage":"archive", "counts":{"succeeded":3}},
    {"run_type":"backfill","data_name":"alpha","stage":"enrich",  "counts":{"succeeded":1}},
]

def push_snapshot(leaves):
    r = requests.post(f"{BASE}/ingest_snapshot", json={"snapshot": leaves}, timeout=10)
    r.raise_for_status()
    print("Pushed snapshot:", r.json())

def main():
    # Start clean (no implicit seeding anymore)
    requests.post(f"{BASE}/store/reset", timeout=10)

    # Flip A → B → A → B ...
    for i in range(6):
        push_snapshot(SNAP_A if i % 2 == 0 else SNAP_B)
        time.sleep(5)  # watch the dashboard update

if __name__ == "__main__":
    main()