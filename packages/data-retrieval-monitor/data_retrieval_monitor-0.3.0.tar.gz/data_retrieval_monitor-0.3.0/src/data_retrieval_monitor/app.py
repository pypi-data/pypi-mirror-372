"""
Data Retrieval Monitor (Dash)
- Pure-yellow KPI = validation failed AND retrieval did NOT fail
- Consistent colors across table, Top Lags, Status Mix
- No "Stale" logic
- Date+time filter (with Reset button) applies to table, charts, logs
- Memory or file storage (atomic writes, JSON cache by mtime)
"""

import os
import json
import time
import shutil
import tempfile
import pathlib
import threading
import random
import string
from datetime import datetime, timezone, timedelta

# Optional fast JSON + compression
try:
    import orjson
except Exception:
    orjson = None

try:
    from flask_compress import Compress
except Exception:
    Compress = None

import pytz
from dateutil import parser as dtparser

# Optional: Polars
try:
    import polars as pl
    HAS_POLARS = True
except Exception:
    HAS_POLARS = False
import pandas as pd

from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
from flask import send_from_directory, jsonify, request

# ----------------------------
# Config via env
# ----------------------------
APP_TITLE = "Data Retrieval Live Monitor"
TIMEZONE = os.getenv("APP_TIMEZONE", "Europe/London")
MOCK_MODE = os.getenv("MOCK_MODE", "1") == "1"
REFRESH_MS = int(os.getenv("REFRESH_MS", "30000"))

STORE_BACKEND = os.getenv("STORE_BACKEND", "memory")   # 'file' | 'memory'
STORE_PATH = os.getenv("STORE_PATH", "status_store.json")
_MEM_STORE = None

LOG_DIR = os.getenv("LOG_DIR", "source_logs")
pathlib.Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

DEFAULT_EXPECTED_EVERY_MIN = int(os.getenv("DEFAULT_EXPECTED_EVERY_MIN", "60"))
DEFAULT_GRACE_MIN = int(os.getenv("DEFAULT_GRACE_MIN", "10"))
MOCK_SOURCE_COUNT = int(os.getenv("MOCK_SOURCE_COUNT", "100"))
USE_POLARS = os.getenv("USE_POLARS", "1") == "1" and HAS_POLARS

STORE_LOCK = threading.RLock()

# Cache for file backend
_STORE_CACHE = None
_STORE_MTIME = None

# Colors
STATUS_COLORS = {
    "Healthy":            "#009E73",  # green
    "Delayed":            "#F0E442",  # yellow
    "Validation Failed":  "#E69F00",  # amber
    "Overdue":            "#D55E00",  # red
    "Retrieve Failed":    "#D55E00",  # red
}

ROW_TINTS = {
    "Healthy":            "#DFF5ED",
    "Delayed":            "#FFFCD1",  # yellow tint
    "Validation Failed":  "#FFEACC",  # amber tint
    "Overdue":            "#FFE1D6",
    "Retrieve Failed":    "#FFE1D6",
}

SEVERITY_RANK = {
    "Retrieve Failed":   4,
    "Overdue":           4,
    "Validation Failed": 3,
    "Delayed":           2,
    "Healthy":           1,
}

# ----------------------------
# Helpers
# ----------------------------
_DEF_TZ = pytz.timezone(TIMEZONE)

def now_tz():
    return datetime.now(_DEF_TZ)

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def to_dt(x):
    if not x:
        return None
    try:
        return dtparser.isoparse(x).astimezone(timezone.utc)
    except Exception:
        return None

def fmt_local_dt(dt_obj):
    if not dt_obj:
        return "—"
    try:
        return dt_obj.astimezone(_DEF_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return "—"

def combine_local_to_utc(date_str, time_str, end=False):
    if not date_str:
        return None
    t = (time_str or ("23:59:59" if end else "00:00:00")).strip()
    if len(t) == 5:
        t = t + ":00"
    try:
        dt_local = datetime.strptime(f"{date_str} {t}", "%Y-%m-%d %H:%M:%S")
        return _DEF_TZ.localize(dt_local).astimezone(timezone.utc)
    except Exception:
        return None

def meta_to_markdown(meta: dict) -> str:
    try:
        if not isinstance(meta, dict):
            return "—"
        parts = []
        for k, v in list(meta.items())[:8]:
            if isinstance(v, str) and (v.lower().startswith("http") or v.startswith("/logs/")):
                label = k if len(k) <= 18 else k[:15] + "…"
                parts.append(f"[{label}]({v})")
            else:
                val = str(v)
                if len(val) > 28:
                    val = val[:25] + "…"
                parts.append(f"**{k}**: `{val}`")
        return " · ".join(parts) if parts else "—"
    except Exception:
        return "—"

def _init_empty_store_dict():
    return {"sources": {}, "logs": [], "updated_at": utc_now_iso()}

def ensure_store_file():
    if STORE_BACKEND == "memory":
        global _MEM_STORE
        if _MEM_STORE is None:
            _MEM_STORE = _init_empty_store_dict()
        return
    with STORE_LOCK:
        path = pathlib.Path(STORE_PATH)
        if not path.exists():
            path.write_text(json.dumps(_init_empty_store_dict(), indent=2))

def _json_load(data: bytes):
    if orjson:
        return orjson.loads(data)
    return json.loads(data.decode("utf-8"))

def _json_dump(obj) -> bytes:
    if orjson:
        return orjson.dumps(obj, option=orjson.OPT_INDENT_2)
    return json.dumps(obj, indent=2).encode("utf-8")

def load_status_store():
    ensure_store_file()
    if STORE_BACKEND == "memory":
        return _MEM_STORE
    global _STORE_CACHE, _STORE_MTIME
    with STORE_LOCK:
        mtime = os.path.getmtime(STORE_PATH)
        if _STORE_CACHE is not None and _STORE_MTIME == mtime:
            return _STORE_CACHE
        with open(STORE_PATH, "rb") as f:
            data = _json_load(f.read())
        _STORE_CACHE, _STORE_MTIME = data, mtime
        return data

def save_status_store(store):
    # cap logs to avoid bloat
    logs = store.setdefault("logs", [])
    if len(logs) > 2000:
        store["logs"] = logs[-2000:]

    store["updated_at"] = utc_now_iso()
    if STORE_BACKEND == "memory":
        with STORE_LOCK:
            global _MEM_STORE
            _MEM_STORE = store
        return
    with STORE_LOCK:
        dir_ = os.path.dirname(os.path.abspath(STORE_PATH)) or "."
        fd, tmp_path = tempfile.mkstemp(prefix="store.", suffix=".tmp", dir=dir_)
        try:
            with os.fdopen(fd, "wb") as tmp:
                tmp.write(_json_dump(store))
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(tmp_path, STORE_PATH)
            # update cache
            global _STORE_CACHE, _STORE_MTIME
            _STORE_CACHE = store
            _STORE_MTIME = os.path.getmtime(STORE_PATH)
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

def _log_path_for_sid(source_id: str) -> str:
    safe = "".join(ch for ch in source_id if ch.isalnum() or ch in ("-", "_"))
    return f"/logs/{safe}.log"

def _ensure_log_file(source_id: str):
    fname = _log_path_for_sid(source_id).split("/logs/")[1]
    fpath = pathlib.Path(LOG_DIR) / fname
    if not fpath.exists():
        fpath.write_text(f"# Log for {source_id}\n", encoding="utf-8")

# ----------------------------
# Seeding / Mock
# ----------------------------
def seed_mock_sources(store):
    base = now_tz() - timedelta(minutes=5)
    mock = [
        dict(
            source_id="alpha_factors_daily",
            name="Alpha Factors (Daily)",
            expected_every_minutes=1440,
            grace_minutes=30,
            last_received_at=(base - timedelta(hours=12)).astimezone(timezone.utc).isoformat(),
            expected_at=(base - timedelta(hours=12) + timedelta(minutes=1440)).astimezone(timezone.utc).isoformat(),
            last_validation_passed=True,
            validation_errors=[],
            run_status="success",
            error_message="",
            meta={"rows": 49230, "file": "alpha_2025-08-25.parquet",
                  "docs": "https://example.com/alpha", "log": _log_path_for_sid("alpha_factors_daily")},
        ),
        dict(
            source_id="prices_hourly",
            name="Prices (Hourly)",
            expected_every_minutes=60,
            grace_minutes=10,
            last_received_at=(base - timedelta(minutes=75)).astimezone(timezone.utc).isoformat(),
            data_reset_at=(base - timedelta(minutes=30)).astimezone(timezone.utc).isoformat(),
            last_validation_passed=False,  # pure yellow example
            validation_errors=["Missing 3 tickers", "NaNs in close for 2 instruments"],
            run_status="success",  # retrieval OK
            error_message="",
            meta={"rows": 118233, "runbook": "https://example.com/prices-runbook",
                  "log": _log_path_for_sid("prices_hourly")},
        ),
        dict(
            source_id="news_stream",
            name="News Stream",
            expected_every_minutes=5,
            grace_minutes=2,
            last_received_at=(base - timedelta(minutes=3)).astimezone(timezone.utc).isoformat(),
            expected_at=(base + timedelta(minutes=2)).astimezone(timezone.utc).isoformat(),
            grace_until=(base + timedelta(minutes=6)).astimezone(timezone.utc).isoformat(),
            last_validation_passed=True,
            validation_errors=[],
            run_status="success",
            error_message="",
            meta={"msgs_last_5_min": 214, "dashboard": "https://example.com/news",
                  "log": _log_path_for_sid("news_stream")},
        ),
        dict(
            source_id="fundamentals_daily",
            name="Fundamentals (Daily)",
            expected_every_minutes=1440,
            grace_minutes=120,
            last_received_at=(base - timedelta(days=2, minutes=10)).astimezone(timezone.utc).isoformat(),
            expected_at=(base - timedelta(days=2, minutes=10) + timedelta(minutes=1440)).astimezone(timezone.utc).isoformat(),
            last_validation_passed=True,
            validation_errors=[],
            run_status="success",
            error_message="",
            meta={"symbols": 4389, "docs": "https://example.com/fundamentals",
                  "log": _log_path_for_sid("fundamentals_daily")},
        ),
        # explicit pure-yellow example
        dict(
            source_id="validation_only_example",
            name="Validation-Only Fail Example",
            expected_every_minutes=60,
            grace_minutes=10,
            last_received_at=(base - timedelta(minutes=12)).astimezone(timezone.utc).isoformat(),
            expected_at=(base + timedelta(minutes=30)).astimezone(timezone.utc).isoformat(),
            last_validation_passed=False,
            validation_errors=["Schema mismatch on 2 fields"],
            run_status="success",
            error_message="",
            meta={"rows": 32000, "docs": "https://example.com/validation-only",
                  "log": _log_path_for_sid("validation_only_example")},
        ),
    ]
    random.seed(42)
    kinds = [("stream", 5, 2), ("hourly", 60, 10), ("daily", 1440, 60)]
    extra = max(0, MOCK_SOURCE_COUNT - len(mock))
    for i in range(extra):
        kind, expected, grace = random.choice(kinds)
        sid = f"mock_{kind}_{i:04d}"
        name = f"Mock {kind.title()} Source {i:04d}"
        if random.random() < 0.6:
            delta = random.randint(0, max(1, expected // 2))
        else:
            delta = expected + grace + random.randint(1, 90)
        last_recv = (base - timedelta(minutes=delta)).astimezone(timezone.utc).isoformat()

        run_status = "failed" if random.random() < 0.05 else "success"
        # ~10% pure yellow
        val_pass = False if random.random() < 0.10 else True
        error = "" if (run_status == "success" and val_pass) else random.choice(
            ["Timeout from vendor API", "ValidationError: NaNs detected", "File missing in S3", "HTTP 500 from upstream"]
        )
        mock.append(dict(
            source_id=sid,
            name=name,
            expected_every_minutes=expected,
            grace_minutes=grace,
            last_received_at=last_recv,
            expected_at=(datetime.now(timezone.utc) + timedelta(minutes=random.randint(1, expected))).isoformat()
                if random.random() < 0.3 else None,
            data_reset_at=(datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, expected))).isoformat()
                if random.random() < 0.2 else None,
            grace_until=(datetime.now(timezone.utc) + timedelta(minutes=random.randint(1, 60))).isoformat()
                if random.random() < 0.2 else None,
            last_validation_passed=val_pass,
            validation_errors=[] if val_pass else ["Auto-detected anomaly"],
            run_status=run_status,
            error_message=error,
            meta={"rows": random.randint(1000, 100000),
                  "link": "https://example.com/source/" + sid,
                  "log": _log_path_for_sid(sid)},
        ))

    store.setdefault("sources", {})
    for s in mock:
        store["sources"][s["source_id"]] = s
        _ensure_log_file(s["source_id"])

    store.setdefault("logs", [])
    store["logs"].append({
        "ts": utc_now_iso(),
        "level": "INFO",
        "msg": f"Initialized mock sources (MOCK_MODE=1, count={len(mock)})",
    })

def _random_id(n=6):
    return "src_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

def _get_int_nullable(payload: dict, item: dict, field: str, default=None):
    if field in payload:
        v = payload[field]
        if v is None or v == "":
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None
    v = item.get(field, None)
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return None

def upsert_source(store, payload: dict):
    sources = store.setdefault("sources", {})
    sid = payload.get("source_id") or _random_id()
    item = sources.get(sid, {})

    item.update({
        "source_id": sid,
        "name": payload.get("name", item.get("name", sid)),
        "expected_every_minutes": _get_int_nullable(payload, item, "expected_every_minutes", None),
        "expected_at": payload.get("expected_at", item.get("expected_at")),
        "data_reset_at": payload.get("data_reset_at", item.get("data_reset_at")),
        "grace_minutes": _get_int_nullable(payload, item, "grace_minutes", None),
        "grace_until": payload.get("grace_until", item.get("grace_until")),
        "last_received_at": payload.get("last_received_at", item.get("last_received_at")),
        "last_validation_passed": bool(payload.get("last_validation_passed", item.get("last_validation_passed", False))),
        "validation_errors": payload.get("validation_errors", item.get("validation_errors", [])),
        "run_status": payload.get("run_status", item.get("run_status", "success")),
        "error_message": payload.get("error_message", item.get("error_message", "")),
        "meta": payload.get("meta", item.get("meta", {})),
        "heartbeat_at": utc_now_iso(),
    })

    _ensure_log_file(sid)

    sources[sid] = item
    store.setdefault("logs", []).append({
        "ts": utc_now_iso(),
        "level": "INFO" if item["run_status"] == "success" else "ERROR",
        "msg": f"[{item['name']}] run_status={item['run_status']} validation={'PASS' if item['last_validation_passed'] else 'FAIL'} last_received_at={item['last_received_at']}",
    })

# ----------------------------
# Health (no Stale)
# ----------------------------
def compute_health_row(s: dict) -> dict:
    now_utc = datetime.now(timezone.utc)
    last = to_dt(s.get("last_received_at"))

    expected_minutes = s.get("expected_every_minutes")
    expected_minutes = int(expected_minutes) if expected_minutes is not None else None

    grace_minutes = s.get("grace_minutes")
    grace_minutes = int(grace_minutes) if grace_minutes is not None else None

    expected_at = to_dt(s.get("expected_at"))
    reset_at = to_dt(s.get("data_reset_at"))
    grace_until = to_dt(s.get("grace_until"))

    if reset_at and (not last or reset_at > last):
        base_time = reset_at
    else:
        base_time = last or reset_at

    if expected_at is not None:
        due = expected_at
    elif expected_minutes is not None and base_time is not None:
        due = base_time + timedelta(minutes=expected_minutes)
    else:
        due = None

    if due is not None and grace_minutes is not None and not grace_until:
        grace_until = due + timedelta(minutes=grace_minutes)
    if due is not None and grace_until is not None and (grace_minutes is None):
        try:
            grace_minutes = max(0, int((grace_until - due).total_seconds() // 60))
        except Exception:
            pass

    mins_since = None
    if last:
        mins_since = int((now_utc - last).total_seconds() // 60)

    retrieve_failed   = (s.get("run_status") == "failed")
    overdue_beyond    = bool(grace_until and now_utc > grace_until)
    delayed_within    = bool(due and (now_utc > due) and (not grace_until or now_utc <= grace_until))
    validation_failed = (not s.get("last_validation_passed", True))

    if retrieve_failed:
        status = "Retrieve Failed"
    elif overdue_beyond:
        status = "Overdue"
    elif validation_failed:
        status = "Validation Failed"
    elif delayed_within:
        status = "Delayed"
    else:
        status = "Healthy"

    severity = SEVERITY_RANK.get(status, 1)

    meta = dict(s.get("meta", {}))
    if "log" not in meta:
        meta["log"] = _log_path_for_sid(s.get("source_id"))

    return {
        "source_id": s.get("source_id"),
        "Source": s.get("name"),
        "Status": status,
        "Severity": severity,
        "Validation": "Pass" if s.get("last_validation_passed", False) else "Fail",
        "Last Received": fmt_local_dt(last),
        "Last Received ISO": s.get("last_received_at") or "",
        "Expected At": fmt_local_dt(due),
        "Expected At ISO": due.isoformat() if due else "",
        "Grace Until": fmt_local_dt(grace_until),
        "Grace Until ISO": grace_until.isoformat() if grace_until else "",
        "Reset At": fmt_local_dt(reset_at),
        "Reset At ISO": s.get("data_reset_at", ""),
        "Minutes Since": mins_since if mins_since is not None else "—",
        "Expected (min)": expected_minutes if expected_minutes is not None else "—",
        "Grace (min)": grace_minutes if grace_minutes is not None else "—",
        "Run Status": s.get("run_status"),
        "Error": s.get("error_message", ""),
        "Meta": meta_to_markdown(meta),
        "Base At": base_time.isoformat() if base_time else "",
        "Deadline At": (grace_until or due).isoformat() if (grace_until or due) else "",
    }

def store_to_dataframe(store: dict):
    sources = store.get("sources", {})
    rows = [compute_health_row(s) for s in sources.values()]

    ordered_cols = [
        "Source", "Status", "Severity", "Validation", "Run Status",
        "Minutes Since", "Expected (min)", "Grace (min)",
        "Expected At", "Expected At ISO", "Grace Until", "Grace Until ISO",
        "Reset At", "Reset At ISO",
        "Last Received", "Last Received ISO",
        "Error", "Meta",
        "Base At", "Deadline At",
        "source_id",
    ]

    if USE_POLARS:
        try:
            df_pl = pl.DataFrame(rows)
            if df_pl.height == 0:
                return pd.DataFrame(columns=ordered_cols)
            for c in ordered_cols:
                if c not in df_pl.columns:
                    df_pl = df_pl.with_columns(pl.lit(None).alias(c))
            df_pl = df_pl.select(ordered_cols)
            return df_pl.to_pandas()
        except Exception:
            pass

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df[ordered_cols]
    else:
        df = pd.DataFrame(columns=ordered_cols)
    return df

# ----------------------------
# Mock churner
# ----------------------------
class MockChurner(threading.Thread):
    daemon = True
    def run(self):
        while True:
            if not MOCK_MODE:
                return
            try:
                store = load_status_store()
                for sid, item in list(store.get("sources", {}).items()):
                    last = to_dt(item.get("last_received_at")) or datetime.now(timezone.utc) - timedelta(minutes=30)
                    last = last + timedelta(minutes=random.randint(0, 15))
                    item["last_received_at"] = last.isoformat()

                    coin = random.random()
                    if coin < 0.07:
                        item["run_status"] = "failed"
                        item["last_validation_passed"] = False
                        item["error_message"] = random.choice([
                            "Timeout from vendor API",
                            "ValidationError: NaNs detected",
                            "File missing in S3",
                            "HTTP 500 from upstream",
                        ])
                    elif coin < 0.12:
                        item["run_status"] = "success"
                        item["last_validation_passed"] = False  # PURE yellow
                        item["error_message"] = "ValidationError: threshold breached"
                    elif coin < 0.45:
                        item["run_status"] = "success"
                        item["last_validation_passed"] = True
                        item["error_message"] = ""

                    store["sources"][sid] = item
                save_status_store(store)
            except Exception:
                pass
            finally:
                time.sleep(40)

# ----------------------------
# Dash App factory
# ----------------------------
def build_app():
    external_stylesheets = [dbc.themes.FLATLY]
    app = Dash(__name__, external_stylesheets=external_stylesheets, title=APP_TITLE)
    server = app.server

    # Optional gzip
    if Compress is not None:
        Compress(server)

    # Routes
    @server.route("/ingest_status", methods=["POST"])
    def ingest_status():
        try:
            payload = request.get_json(force=True, silent=False)
            store = load_status_store()
            if isinstance(payload, list):
                for p in payload:
                    upsert_source(store, p)
            elif isinstance(payload, dict):
                upsert_source(store, payload)
            else:
                return jsonify({"ok": False, "error": "Payload must be object or array"}), 400
            save_status_store(store)
            return jsonify({"ok": True})
        except Exception as e:
            return ({"ok": False, "error": str(e)}, 400)

    @server.route("/logs/<path:filename>")
    def serve_logs(filename):
        return send_from_directory(LOG_DIR, filename, mimetype="text/plain", as_attachment=False)

    @server.get("/store/export")
    def export_store():
        store = load_status_store()
        return jsonify(store)

    @server.post("/store/import")
    def import_store():
        payload = request.get_json(force=True, silent=False)
        if not isinstance(payload, dict) or "sources" not in payload or "logs" not in payload:
            return jsonify({"ok": False, "error": "Payload must be dict with 'sources' and 'logs'"}), 400
        save_status_store(payload)
        return jsonify({"ok": True})

    @server.post("/store/reset")
    def reset_store():
        store = _init_empty_store_dict()
        if MOCK_MODE:
            seed_mock_sources(store)
        save_status_store(store)
        return jsonify({"ok": True})

    @server.get("/healthz")
    def health():
        store = load_status_store()
        n = len(store.get("sources", {}))
        logs = len(store.get("logs", []))
        size = 0
        if STORE_BACKEND == "file" and os.path.exists(STORE_PATH):
            size = os.path.getsize(STORE_PATH)
        return jsonify({"ok": True, "sources": n, "logs": logs, "store_bytes": size, "backend": STORE_BACKEND})

    # Layout
    app.layout = dbc.Container([
        dcc.Store(id="store-refresh-timestamp"),
        html.Div(style={"height": "14px"}),
        dbc.Row([
            dbc.Col(html.H2(APP_TITLE, className="fw-bold"), md=8),
            dbc.Col(html.Div(id="now-indicator", className="text-end text-muted"), md=4),
        ], align="center"),

        html.Hr(),

        # KPI cards
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody([
                html.Div("Sources", className="text-muted small"),
                html.H3(id="metric-sources", className="mb-0 fw-semibold"),
            ])]), md=2),
            dbc.Col(dbc.Card([dbc.CardBody([
                html.Div("Healthy (Green)", className="text-muted small"),
                html.H3(id="metric-healthy", className="mb-0 fw-semibold"),
            ])]), md=2),
            dbc.Col(dbc.Card([dbc.CardBody([
                html.Div("Yellow (Delayed)", className="text-muted small"),
                html.H3(id="metric-delayed", className="mb-0 fw-semibold"),
            ])]), md=2),
            dbc.Col(dbc.Card([dbc.CardBody([
                html.Div("Amber (Validation Failed)", className="text-muted small"),
                html.H3(id="metric-yellow", className="mb-0 fw-semibold"),
            ])]), md=3),
            dbc.Col(dbc.Card([dbc.CardBody([
                html.Div("Red (Overdue/Failed)", className="text-muted small"),
                html.H3(id="metric-failed", className="mb-0 fw-semibold"),
            ])]), md=3),
        ], className="gy-3"),

        html.Div(style={"height": "12px"}),

        # Filters
        dbc.Row([
            dbc.Col([
                html.Label("Filter by status"),
                dcc.Dropdown(
                    id="status-filter",
                    options=[{"label": s, "value": s} for s in
                             ["All", "Healthy", "Delayed", "Validation Failed", "Overdue", "Retrieve Failed"]],
                    value="All", clearable=False,
                ),
            ], md=3),
            dbc.Col([
                html.Label("Search by source name"),
                dcc.Input(id="text-filter", placeholder="e.g. Alpha", type="text", debounce=True, className="form-control"),
            ], md=3),
            dbc.Col([
                html.Label("Sort by"),
                dcc.Dropdown(
                    id="sort-mode",
                    options=[
                        {"label": "None", "value": "none"},
                        {"label": "Status Color (severity: Red→Yellow/Amber→Green)", "value": "severity_desc"},
                        {"label": "Status Color (severity: Green→Amber/Yellow→Red)", "value": "severity_asc"},
                    ],
                    value="none", clearable=False,
                ),
            ], md=3),
            dbc.Col([
                html.Label("Auto-refresh"),
                dcc.Slider(
                    id="refresh-slider", min=5, max=120, step=5, value=REFRESH_MS // 1000,
                    marks=None, tooltip={"placement": "bottom", "always_visible": False},
                ),
                html.Small("Refresh interval (seconds)", className="text-muted"),
            ], md=3),
        ]),

        html.Div(style={"height": "10px"}),

        # Charts row
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="status-pie", style={"height": "520px"}, config={"responsive": True}),
            ], md=6),
            dbc.Col([
                html.Div([
                    dcc.Checklist(
                        id="overdue-only",
                        options=[{"label": "Show only issues (Red / Amber / Yellow)", "value": "issues"}],
                        value=["issues"],
                        inputStyle={"marginRight": "6px"},
                        style={"fontSize": "13px", "marginBottom": "4px"},
                    ),
                    html.Label("Top lags: number of bars"),
                    dcc.Dropdown(
                        id="top-lags-n",
                        options=[{"label": str(n), "value": n} for n in [10, 15, 20, 30, 50, 100]],
                        value=15, clearable=False, style={"maxWidth": "140px"},
                    ),
                    html.Small("Scroll appears if bars > ~20", className="text-muted d-block"),
                ]),
                html.Div([dcc.Graph(id="lag-bar")],
                         id="lag-wrap",
                         style={"maxHeight": "700px", "overflowY": "auto"}),
            ], md=6),
        ], className="gy-3"),

        html.Div(style={"height": "10px"}),

        # Logs controls + modal (+ reset)
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Recent log messages", className="fw-semibold d-inline me-3"),
                    dbc.Button("Open logs", id="open-logs", size="sm", className="btn-primary me-3"),
                    html.Span("Filter (applies to logs & dashboard):", className="me-2"),
                    dcc.DatePickerRange(id="logs-date-range", display_format="YYYY-MM-DD", className="me-2"),
                    dbc.Input(id="logs-start-time", type="time", value="00:00", step=1, style={"width": "140px"}, className="me-2"),
                    dbc.Input(id="logs-end-time",   type="time", value="23:59", step=1, style={"width": "140px"}, className="me-2"),
                    dbc.Button("Reset date/time filter", id="reset-datetime-filter",
                               color="secondary", outline=True, size="sm", className="ms-2"),
                ], className="d-flex align-items-center flex-wrap gap-2"),
            ])
        ]),

        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Recent log messages")),
            dbc.ModalBody(html.Div(
                id="logs-pane-modal",
                style={"maxHeight": "70vh", "overflowY": "auto",
                       "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Monaco", "fontSize": "13px"}
            )),
            dbc.ModalFooter(dbc.Button("Close", id="close-logs", className="ms-auto")),
        ], id="logs-modal", is_open=False, size="xl", scrollable=True),

        html.Div(style={"height": "10px"}),

        # Table controls
        dbc.Row([
            dbc.Col(html.Div(id="table-summary", className="text-muted small"), md=6),
            dbc.Col([
                html.Label("Entries per page", className="me-2"),
                dcc.Dropdown(
                    id="entries-per-page",
                    options=[{"label": str(n), "value": n} for n in [10, 25, 50, 100, 200]],
                    value=25, clearable=False,
                    style={"display": "inline-block", "minWidth": "120px", "maxWidth": "200px"},
                ),
            ], md=6, className="text-end"),
        ]),

        html.Div(style={"height": "6px"}),

        # Main status board
        dbc.Row([
            dbc.Col([
                dash_table.DataTable(
                    id="sources-table",
                    page_size=25,
                    page_action="native",
                    sort_action="native",
                    filter_action="native",
                    markdown_options={"link_target": "_blank"},
                    columns=[
                        {"name": "Source", "id": "Source"},
                        {"name": "Status", "id": "Status"},
                        {"name": "Severity", "id": "Severity", "type": "numeric"},
                        {"name": "Validation", "id": "Validation"},
                        {"name": "Run Status", "id": "Run Status"},
                        {"name": "Minutes Since", "id": "Minutes Since", "type": "numeric"},
                        {"name": "Expected (min)", "id": "Expected (min)", "type": "numeric"},
                        {"name": "Grace (min)", "id": "Grace (min)", "type": "numeric"},
                        {"name": "Expected At", "id": "Expected At"},
                        {"name": "Grace Until", "id": "Grace Until"},
                        {"name": "Reset At", "id": "Reset At"},
                        {"name": "Last Received", "id": "Last Received"},
                        {"name": "Error", "id": "Error"},
                        {"name": "Meta", "id": "Meta", "presentation": "markdown"},
                        {"name": "Expected At ISO", "id": "Expected At ISO"},
                        {"name": "Grace Until ISO", "id": "Grace Until ISO"},
                        {"name": "Reset At ISO", "id": "Reset At ISO"},
                        {"name": "Last Received ISO", "id": "Last Received ISO"},
                        {"name": "Base At", "id": "Base At"},
                        {"name": "Deadline At", "id": "Deadline At"},
                        {"name": "source_id", "id": "source_id"},
                    ],
                    hidden_columns=[
                        "Severity", "source_id",
                        "Expected At ISO", "Grace Until ISO", "Reset At ISO", "Last Received ISO",
                        "Base At", "Deadline At"
                    ],
                    style_table={"overflowX": "auto"},
                    style_cell={"fontFamily": "Inter, system-ui, sans-serif", "fontSize": 14, "padding": "8px"},
                    style_header={"fontWeight": "bold"},
                    style_data_conditional=[
                        {"if": {"filter_query": "{Status} = 'Healthy'"},
                         "backgroundColor": ROW_TINTS["Healthy"]},
                        {"if": {"filter_query": "{Status} = 'Delayed'"},
                         "backgroundColor": ROW_TINTS["Delayed"]},
                        {"if": {"filter_query": "{Status} = 'Validation Failed'"},
                         "backgroundColor": ROW_TINTS["Validation Failed"], "color": "#333"},
                        {"if": {"filter_query": "{Validation} = 'Fail'"},
                         "backgroundColor": ROW_TINTS["Validation Failed"], "color": "#333"},
                        {"if": {"filter_query": "{Status} = 'Overdue'"},
                         "backgroundColor": ROW_TINTS["Overdue"]},
                        {"if": {"filter_query": "{Status} = 'Retrieve Failed'"},
                         "backgroundColor": ROW_TINTS["Retrieve Failed"]},
                        {"if": {"filter_query": "{Validation} = 'Pass'", "column_id": "Validation"},
                         "color": STATUS_COLORS["Healthy"], "fontWeight": "700"},
                        {"if": {"filter_query": "{Validation} = 'Fail'", "column_id": "Validation"},
                         "color": "#333", "fontWeight": "800"},
                    ],
                )
            ], md=12)
        ]),

        dcc.Interval(id="interval", interval=REFRESH_MS, n_intervals=0),
    ], fluid=True, className="pt-3 pb-5")

    # Callbacks
    @app.callback(
        Output("logs-modal", "is_open"),
        Input("open-logs", "n_clicks"),
        Input("close-logs", "n_clicks"),
        prevent_initial_call=False,
    )
    def toggle_logs_modal(open_clicks, close_clicks):
        if close_clicks:
            return False
        if open_clicks:
            return True
        return False

    @app.callback(
        Output("logs-date-range", "start_date"),
        Output("logs-date-range", "end_date"),
        Output("logs-start-time", "value"),
        Output("logs-end-time", "value"),
        Input("reset-datetime-filter", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_datetime_filter(_):
        return None, None, "00:00", "23:59"

    @app.callback(
        Output("metric-sources", "children"),
        Output("metric-healthy", "children"),
        Output("metric-delayed", "children"),
        Output("metric-yellow", "children"),   # PURE yellow
        Output("metric-failed", "children"),
        Output("sources-table", "data"),
        Output("sources-table", "page_size"),
        Output("lag-bar", "figure"),
        Output("status-pie", "figure"),
        Output("logs-pane-modal", "children"),
        Output("table-summary", "children"),
        Output("now-indicator", "children"),
        Output("interval", "interval"),
        Input("interval", "n_intervals"),
        Input("status-filter", "value"),
        Input("text-filter", "value"),
        Input("sort-mode", "value"),
        Input("refresh-slider", "value"),
        Input("overdue-only", "value"),
        Input("entries-per-page", "value"),
        Input("top-lags-n", "value"),
        Input("logs-date-range", "start_date"),
        Input("logs-date-range", "end_date"),
        Input("logs-start-time", "value"),
        Input("logs-end-time", "value"),
    )
    def refresh(_n, status_filter, text_filter, sort_mode, refresh_seconds, overdue_value,
                entries_per_page, top_lags_n, logs_start_date, logs_end_date,
                logs_start_time, logs_end_time):

        interval_ms = max(5, int(refresh_seconds)) * 1000

        store = load_status_store()
        if MOCK_MODE and not store.get("sources"):
            seed_mock_sources(store)
            save_status_store(store)

        df = store_to_dataframe(store)

        # normalize any legacy strings
        if not df.empty and "Status" in df.columns:
            df["Status"] = df["Status"].replace({
                "Stale": "Delayed",
                "Failed": "Retrieve Failed",
            })

        # Dashboard-wide datetime filter
        start_dt_utc = combine_local_to_utc(logs_start_date, logs_start_time, end=False)
        end_dt_utc   = combine_local_to_utc(logs_end_date,   logs_end_time,   end=True)

        if (start_dt_utc is not None) or (end_dt_utc is not None):
            def _pick_ref_dt(row):
                for c in ["Last Received ISO", "Expected At ISO", "Grace Until ISO", "Reset At ISO"]:
                    iso = row.get(c)
                    if iso:
                        dt = to_dt(iso)
                        if dt:
                            return dt
                return None
            if not df.empty:
                ref = df.apply(_pick_ref_dt, axis=1)
                mask = ref.notna()
                if start_dt_utc is not None:
                    mask &= (ref >= start_dt_utc)
                if end_dt_utc is not None:
                    mask &= (ref <= end_dt_utc)
                df = df[mask]

        # text/status filter
        if not df.empty:
            if status_filter and status_filter != "All":
                df = df[df["Status"] == status_filter]
            if text_filter:
                df = df[df["Source"].str.contains(str(text_filter), case=False, na=False)]

        # sort by severity
        if not df.empty and sort_mode and sort_mode != "none":
            ascending = (sort_mode == "severity_asc")
            df = df.sort_values(["Severity", "Source"], ascending=[ascending, True])

        # KPIs
        total   = len(df)
        healthy = int((df["Status"] == "Healthy").sum()) if not df.empty else 0
        amber   = int((df["Status"] == "Delayed").sum()) if not df.empty else 0

        # PURE validation failures (exclude Overdue/Retrieve Failed entirely)
        if not df.empty:
            yellow_pure = int((df["Status"] == "Validation Failed").sum())
            red = int(df["Status"].isin(["Overdue", "Retrieve Failed"]).sum())
        else:
            yellow_pure = 0
            red = 0

        table_data = df.to_dict("records") if not df.empty else []

        # Top Lags
        if not df.empty:
            tz_local = _DEF_TZ
            lag_df = df.copy()
            lag_df["Minutes Since"] = pd.to_numeric(lag_df["Minutes Since"], errors="coerce").fillna(0)

            only_issues = bool(overdue_value and "issues" in overdue_value)
            if only_issues:
                lag_df = lag_df[lag_df["Status"].isin(["Overdue", "Retrieve Failed", "Delayed", "Validation Failed"])]

            def _allowed_minutes(row):
                try:
                    em = pd.to_numeric(row.get("Expected (min)"))
                except Exception:
                    em = None
                try:
                    gm = pd.to_numeric(row.get("Grace (min)"))
                except Exception:
                    gm = None
                if pd.notnull(em) and pd.notnull(gm):
                    return int(em + gm)
                base = to_dt(row.get("Base At"))
                dl = to_dt(row.get("Deadline At"))
                if base and dl:
                    return max(0, int((dl - base).total_seconds() // 60))
                return None

            lag_df["Exp+Grace"] = lag_df.apply(_allowed_minutes, axis=1)

            def _fmt_local_iso(s):
                dt = to_dt(s)
                if dt is None:
                    return "—"
                return dt.astimezone(tz_local).strftime("%Y-%m-%d %H:%M:%S %Z")

            lag_df["Last Local"] = lag_df["Last Received ISO"].apply(_fmt_local_iso)
            lag_n = int(top_lags_n or 15)
            lag_df = lag_df.sort_values("Minutes Since", ascending=False).head(lag_n)

            bar_colors = [STATUS_COLORS.get(s, "#777777") for s in lag_df["Status"]]
            custom = list(zip(lag_df["Status"], lag_df["Exp+Grace"], lag_df["Last Local"]))

            fig_lag = {
                "data": [{
                    "type": "bar",
                    "x": lag_df["Minutes Since"],
                    "y": lag_df["Source"],
                    "orientation": "h",
                    "text": lag_df["Minutes Since"].astype(int).astype(str) + " min",
                    "textposition": "outside",
                    "marker": {"color": bar_colors},
                    "customdata": custom,
                    "hovertemplate": (
                        "<b>%{y}</b><br>"
                        "Status: %{customdata[0]}<br>"
                        "Minutes since: %{x} min<br>"
                        "Expected+grace: %{customdata[1]} min<br>"
                        "Last received: %{customdata[2]}<extra></extra>"
                    ),
                }],
                "layout": {
                    "title": f"Top Lags (minutes since last received) — Top {lag_n}",
                    "xaxis": {"title": "Minutes since last received (min)", "automargin": True, "gridcolor": "#eee"},
                    "yaxis": {"automargin": True},
                    "uniformtext": {"minsize": 10, "mode": "hide"},
                    "margin": {"l": 200, "r": 20, "t": 50, "b": 40},
                    "height": max(200, 28 * len(lag_df) + 140),
                },
            }
        else:
            fig_lag = {"data": [], "layout": {"title": "Top Lags (minutes since last received)"}}

        # Status Mix
        if not df.empty:
            order = ["Retrieve Failed", "Overdue", "Validation Failed", "Delayed", "Healthy"]
            counts = df["Status"].value_counts()
            labels = [lbl for lbl in order if lbl in counts.index]
            values = [int(counts[lbl]) for lbl in labels]
            colors = [STATUS_COLORS[lbl] for lbl in labels]
            fig_pie = {
                "data": [{
                    "type": "pie",
                    "labels": labels,
                    "values": values,
                    "hole": 0.45,
                    "marker": {"colors": colors},
                    "hovertemplate": "%{label}: %{value} sources<extra></extra>",
                }],
                "layout": {"title": "Status Mix", "height": 520},
            }
        else:
            fig_pie = {"data": [], "layout": {"title": "Status Mix", "height": 520}}

        # Logs (apply same datetime range)
        logs = store.get("logs", [])
        filtered_logs = []
        for rec in logs:
            ts = rec.get("ts")
            dt = to_dt(ts)
            if dt is None:
                continue
            if start_dt_utc and dt < start_dt_utc:
                continue
            if end_dt_utc and dt > end_dt_utc:
                continue
            rec_disp = dict(rec)
            rec_disp["ts"] = fmt_local_dt(dt)
            filtered_logs.append(rec_disp)

        filtered_logs = filtered_logs[-500:]
        logs_view = []
        for rec in reversed(filtered_logs):
            ts = rec.get("ts")
            lvl = rec.get("level", "INFO")
            msg = rec.get("msg", "")
            if lvl == "ERROR":
                color = STATUS_COLORS["Overdue"]; bg = ROW_TINTS["Overdue"]
            elif lvl == "INFO":
                color = STATUS_COLORS["Healthy"]; bg = ROW_TINTS["Healthy"]
            else:
                color = "#1b1e21"; bg = "#ececec"
            logs_view.append(html.Div([
                html.Code(f"{ts} [{lvl}] ", style={"fontWeight": "bold"}),
                html.Span(msg),
            ], style={"background": bg, "color": color, "padding": "4px 8px",
                      "borderRadius": "6px", "marginBottom": "6px"}))

        now_local = now_tz().strftime("%Y-%m-%d %H:%M:%S %Z")
        table_summary = f"{total} sources · {healthy} green · {amber} yellow · {yellow_pure} amber · {red} red · {int(entries_per_page or 25)} per page"

        return (
            str(total), str(healthy), str(amber), str(yellow_pure), str(red),
            table_data, int(entries_per_page or 25),
            fig_lag, fig_pie, logs_view, table_summary, f"Refreshed: {now_local}", interval_ms,
        )

    if MOCK_MODE:
        MockChurner().start()

    return app