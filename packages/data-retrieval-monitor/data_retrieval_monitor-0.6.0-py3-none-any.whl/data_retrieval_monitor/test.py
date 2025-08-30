# tester_even.py
import time
import requests

BASE = "http://127.0.0.1:8050"
N = 120  # multiple of 6 makes perfect evenness

OWNERS = ["owner-a", "owner-b"]
MODES  = ["live", "backfill"]
STAGES = ["stage", "archive", "enrich", "consolidate"]
STATUSES = ["failed", "overdue", "retry", "running", "wait", "succeeded"]

def dataset_name(i): return f"dataset-{i:03d}"

def make_chunks(base_offset: int, extra: int = 0, with_links: bool = True):
    """
    Build a small set of chunks whose statuses rotate through STATUSES to keep things even.
    base_offset and extra help shift the pattern between datasets/stages/versions.
    """
    chunks = []
    # 3 chunks per stage; you can adjust if you want more density
    for j in range(3):
        st = STATUSES[(base_offset + j + extra) % len(STATUSES)]
        cid = f"c{j}"
        ch = {"id": cid, "status": st}
        if with_links:
            ch["proc"] = f"https://proc.example/{st}/{base_offset}-{j}"
            ch["log"]  = f"https://logs.example/{st}/{base_offset}-{j}"
        chunks.append(ch)
    return chunks

def build_snapshot(version_offset: int):
    """
    Create a full snapshot for all datasets.
    version_offset changes each loop so the pattern moves (visually shows updates).
    """
    items = []
    for i in range(N):
        owner = OWNERS[i % len(OWNERS)]
        mode  = MODES[(i // len(OWNERS)) % len(MODES)]  # spread evenly across owners x modes
        dn    = dataset_name(i)

        for s_idx, stage in enumerate(STAGES):
            # offset formula ensures even spread across statuses AND variation by version
            offset = (i + s_idx + version_offset) % len(STATUSES)
            chunks = make_chunks(offset, extra=s_idx, with_links=True)
            items.append({
                "owner": owner,
                "mode": mode,
                "data_name": dn,
                "stage": stage,
                "chunks": chunks,
            })
    return items

def push(items):
    r = requests.post(f"{BASE}/feed", json=items, timeout=30)
    r.raise_for_status()
    print(f"pushed {len(items)} stage entries across {N} datasets:", r.json())

def main():
    print("Sending evenly-distributed feeds. Ctrl+C to stop.")
    version = 0
    while True:
        payload = build_snapshot(version)
        push(payload)
        version = (version + 1) % len(STATUSES)  # shift pattern each round
        time.sleep(3)

if __name__ == "__main__":
    main()