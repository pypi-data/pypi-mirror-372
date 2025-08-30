import argparse
import json
import random
import time
from typing import List
import requests

DEFAULT_URL = "http://127.0.0.1:8050/ingest_job_event"
ALL_STAGES = ["stage", "archive", "enrich"]
ALL_STATUS = ["wait", "retry", "running", "failed", "overdue", "succeeded"]

def post(url: str, payload):
    r = requests.post(url, headers={"Content-Type":"application/json"},
                      data=json.dumps(payload), timeout=10)
    r.raise_for_status()
    return r.json()

def seed_fixed(url: str):
    demo = [
        {"run_type":"live","data_name":"prices","stage":"stage","status":"running","count":5},
        {"run_type":"live","data_name":"prices","stage":"archive","status":"wait","count":5},
        {"run_type":"live","data_name":"prices","stage":"enrich","status":"wait","count":5},

        {"run_type":"live","data_name":"alpha","stage":"stage","status":"overdue","count":2},
        {"run_type":"live","data_name":"alpha","stage":"archive","status":"wait","count":1},
        {"run_type":"live","data_name":"alpha","stage":"enrich","status":"wait","count":1},

        {"run_type":"backfill","data_name":"alpha","stage":"stage","status":"retry","count":2},
        {"run_type":"backfill","data_name":"alpha","stage":"archive","status":"wait","count":3},
        {"run_type":"backfill","data_name":"alpha","stage":"enrich","status":"failed","count":1},

        {"run_type":"live","data_name":"beta","stage":"stage","status":"wait","count":9},
        {"run_type":"live","data_name":"beta","stage":"archive","status":"wait","count":1},
        {"run_type":"live","data_name":"beta","stage":"enrich","status":"succeeded","count":12},
    ]
    return post(url, demo)

def stream_random(url: str, batches: int, sleep_secs: float, datasets: List[str]):
    rts = ["live", "backfill"]
    for _ in range(batches):
        payload = {
            "run_type": random.choice(rts),
            "data_name": random.choice(datasets),
            "stage": random.choice(ALL_STAGES),
            "status": random.choices(ALL_STATUS, weights=[5,3,4,2,1,6])[0],
            "count": random.randint(1,4),
        }
        try:
            print("sending:", payload)
            post(url, payload)
        except Exception as e:
            print("send failed:", e)
        time.sleep(sleep_secs)

def main():
    p = argparse.ArgumentParser(prog="drm-injector",
                                description="Inject demo or custom job events into the dashboard")
    p.add_argument("--url", default=DEFAULT_URL, help="POST endpoint (default: %(default)s)")
    sub = p.add_subparsers(dest="cmd", required=False)

    s_fixed = sub.add_parser("fixed", help="Send a fixed demo story (one shot)")
    s_fixed.set_defaults(cmd="fixed")

    s_stream = sub.add_parser("stream", help="Send random stream")
    s_stream.add_argument("--batches", type=int, default=50)
    s_stream.add_argument("--sleep", type=float, default=2.0)
    s_stream.add_argument("--datasets", default="prices,alpha,beta,gamma,delta",
                          help="Comma-separated names")

    s_file = sub.add_parser("file", help="Send events from a JSON file (object or array)")
    s_file.add_argument("path", help="Path to JSON file")

    args = p.parse_args()
    url = args.url

    if args.cmd == "fixed" or args.cmd is None:
        print(seed_fixed(url))
        return

    if args.cmd == "stream":
        ds = [x.strip() for x in args.datasets.split(",") if x.strip()]
        stream_random(url, batches=args.batches, sleep_secs=args.sleep, datasets=ds)
        return

    if args.cmd == "file":
        with open(args.path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        print(post(url, payload))
        return

if __name__ == "__main__":
    main()