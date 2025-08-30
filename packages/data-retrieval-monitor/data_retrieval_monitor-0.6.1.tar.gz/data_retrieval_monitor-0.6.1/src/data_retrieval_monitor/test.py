# test.py
# Minimal feeder for the new app: posts to /feed (same as /ingest_snapshot).
# Runs forever, flipping A/B payloads so the dashboard visibly updates.

import argparse
import random
import time
import requests

# ---------- Easy-to-tweak defaults ----------
DEFAULT_BASE   = "http://127.0.0.1:8060"
OWNERS_DEFAULT = ["owner-a", "owner-b"]
MODES_DEFAULT  = ["live", "backfill"]
N_DATASETS     = 60
SLEEP_SEC      = 3

STAGES = ["stage", "archive", "enrich", "consolidate"]

# Match app’s status set (aliases will be normalized server-side)
ALL_STATUSES = ["failed", "overdue", "manual", "retry", "running", "waiting", "succeeded"]
ALIASES      = ["retrying", "delayed"]  # app maps to retry -> waiting

random.seed(7)


def chunks_for_version(version, i, owner, mode, dn, stage):
    """
    Build a small chunk list for (dataset i, stage) that changes with version.
    Ensures we hit a wide mix of statuses and include proc/log links.
    """
    items = []
    # Base pattern varies with dataset index and stage so rows differ nicely
    base = (i + len(stage)) % 4 + 1  # 1..4 chunks

    if version == 0:
        # Early pipeline feel: stage running/waiting, some retry/manual sprinkled
        candidates = ["running", "waiting", "retry", "manual"]
        if i % 9 == 0:
            candidates.append("overdue")
        if i % 14 == 0:
            candidates.append("failed")
    else:
        # Later pipeline feel: more succeeded, some running/failed/overdue/manual
        candidates = ["succeeded", "running", "manual"]
        if i % 5 == 0:
            candidates.append("failed")
        if i % 7 == 0:
            candidates.append("overdue")
        if i % 11 == 0:
            candidates.append("retry")

    # Occasionally drop in alias statuses to prove normalization works
    if (i + len(stage)) % 13 == 0:
        candidates.append(random.choice(ALIASES))

    for idx in range(base):
        st = random.choice(candidates)
        cid = f"c{idx}"
        items.append({
            "id": cid,
            "status": st,
            "proc": f"https://proc.example/{owner}/{mode}/{dn}/{stage}/{cid}",
            "log":  f"https://logs.example/{owner}/{mode}/{dn}/{stage}/{cid}.log"
        })

    # ~1 in 20 datasets gets an empty chunk list on one stage to test empty display
    if (i + len(stage)) % 20 == 0:
        return []

    return items


def build_feed(version, owners, modes, n):
    """Return a list of stage objects for snapshot ingestion."""
    items = []
    for i in range(n):
        dn     = f"dataset-{i:03d}"
        owner  = owners[i % len(owners)]
        mode   = modes[i % len(modes)]
        for stg in STAGES:
            items.append({
                "owner": owner,
                "mode": mode,
                "data_name": dn,
                "stage": stg,
                "chunks": chunks_for_version(version, i, owner, mode, dn, stg)
            })
    return items


def push(base, items):
    # Prefer /feed (your app routes it to /ingest_snapshot)
    url = f"{base.rstrip('/')}/feed"
    r = requests.post(url, json=items, timeout=30)
    if r.status_code >= 400:
        # Fallback to /ingest_snapshot with {"snapshot": [...]}
        url2 = f"{base.rstrip('/')}/ingest_snapshot"
        r = requests.post(url2, json={"snapshot": items}, timeout=30)
    r.raise_for_status()
    print(f"pushed {len(items)} stage entries across snapshot → {r.json()}")


def reset(base):
    try:
        r = requests.post(f"{base.rstrip('/')}/store/reset", timeout=10)
        print("reset:", r.status_code, r.text)
    except Exception as e:
        print("reset failed (continuing):", e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE, help="App base URL (default: %(default)s)")
    ap.add_argument("--owners", nargs="*", default=OWNERS_DEFAULT, help="Owner list")
    ap.add_argument("--modes",  nargs="*", default=MODES_DEFAULT,  help="Mode list")
    ap.add_argument("--n", type=int, default=N_DATASETS, help="Number of datasets")
    ap.add_argument("--sleep", type=float, default=SLEEP_SEC, help="Seconds between pushes")
    args = ap.parse_args()

    print(f"Base: {args.base}")
    print(f"Owners: {args.owners}")
    print(f"Modes: {args.modes}")
    print(f"Datasets: {args.n}")
    print(f"Interval: {args.sleep}s\n")

    reset(args.base)

    ver = 0
    while True:
        items = build_feed(ver, args.owners, args.modes, args.n)
        push(args.base, items)
        ver ^= 1
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()