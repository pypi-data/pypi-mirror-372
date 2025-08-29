"""
Data Monitor DRM — single-file Dash app with snapshot support.

Features
- Single fixed-width, collapsible table with 3 levels:
    (Live / Backfill) → (Dataset) → (Stage | Archive | Enrich)
- Two Status Mix pies (Live & Backfill)
- KPI & pie clicks expand only relevant rows (collapse-all first)
- "Collapse all" button
- Open rows persist across refresh (session Store)
- Ingestion endpoints:
    - POST /ingest_job_event  (object or array); add ?reset=1 or {"__reset__":true} to clear first
    - POST /ingest_snapshot   (object with {"snapshot":[...] } or an array) replaces ALL state
    - POST /store/reset       (reinit; seeds demo if MOCK_MODE=1)
Environment
- APP_TIMEZONE (default Europe/London)
- MOCK_MODE=0/1 (default 1 → will seed demo once when empty; set 0 to stop seeding)
- REFRESH_MS (default 30000)
- STORE_BACKEND=memory|file (default memory)
- STORE_PATH=path/to/status_store.json (only used if STORE_BACKEND=file)
"""

import os, json, tempfile, pathlib, threading
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import pytz
from dash import Dash, html, dcc, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
from flask import request, jsonify

# ---------- Config ----------
APP_TITLE   = "Job Status Monitor"
TIMEZONE    = os.getenv("APP_TIMEZONE", "Europe/London")
_DEF_TZ     = pytz.timezone(TIMEZONE)
MOCK_MODE   = os.getenv("MOCK_MODE", "1") == "1"
REFRESH_MS  = int(os.getenv("REFRESH_MS", "30000"))
STORE_BACKEND = os.getenv("STORE_BACKEND", "memory")  # memory | file
STORE_PATH  = os.getenv("STORE_PATH", "status_store.json")

# ---------- Job status colors ----------
JOB_STATUS_ORDER = ["wait", "retry", "running", "failed", "overdue", "succeeded"]
JOB_COLORS = {
    "wait":      "#F0E442",  # yellow
    "retry":     "#E69F00",  # orange
    "running":   "#56B4E9",  # blue
    "failed":    "#D55E00",  # red
    "overdue":   "#A50E0E",  # dark red
    "succeeded": "#009E73",  # green
}
def _hex_to_rgb(h): h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
JOB_RGB = {k: _hex_to_rgb(v) for k, v in JOB_COLORS.items()}

# ---------- Store helpers ----------
STORE_LOCK = threading.RLock()
_MEM_STORE = None
_STORE_CACHE = None
_STORE_MTIME = None

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def _init_store(): return {"jobs": {}, "logs": [], "updated_at": utc_now_iso()}

def ensure_store():
    global _MEM_STORE
    if STORE_BACKEND == "memory":
        if _MEM_STORE is None: _MEM_STORE = _init_store()
        return
    p = pathlib.Path(STORE_PATH)
    if not p.exists():
        p.write_text(json.dumps(_init_store(), indent=2))

def load_store():
    ensure_store()
    if STORE_BACKEND == "memory":
        return _MEM_STORE
    global _STORE_CACHE, _STORE_MTIME
    with STORE_LOCK:
        mtime = os.path.getmtime(STORE_PATH)
        if _STORE_CACHE is not None and _STORE_MTIME == mtime:
            return _STORE_CACHE
        with open(STORE_PATH, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
        _STORE_CACHE, _STORE_MTIME = data, mtime
        return data

def save_store(store):
    store["updated_at"] = utc_now_iso()
    logs = store.setdefault("logs", [])
    if len(logs) > 2000: store["logs"] = logs[-2000:]
    if STORE_BACKEND == "memory":
        global _MEM_STORE
        with STORE_LOCK: _MEM_STORE = store
        return
    with STORE_LOCK:
        dir_ = os.path.dirname(os.path.abspath(STORE_PATH)) or "."
        fd, tmp = tempfile.mkstemp(prefix="store.", suffix=".tmp", dir=dir_)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as w:
                json.dump(store, w, indent=2)
                w.flush()
                os.fsync(w.fileno())
            os.replace(tmp, STORE_PATH)
            global _STORE_CACHE, _STORE_MTIME
            _STORE_CACHE = store
            _STORE_MTIME = os.path.getmtime(STORE_PATH)
        finally:
            try:
                if os.path.exists(tmp): os.remove(tmp)
            except Exception:
                pass

# ---------- Ingestion & ensuring all 3 stages ----------
ALL_STAGES = ["stage", "archive", "enrich"]

def _ensure_leaf(store: dict, run_type: str, data_name: str, stage: str) -> Dict:
    jobs = store.setdefault("jobs", {})
    rt = jobs.setdefault(run_type, {})
    dn = rt.setdefault(data_name, {})
    return dn.setdefault(stage, {**{k:0 for k in JOB_STATUS_ORDER}, "errors":[]})

def _ensure_all_stages(store: dict, run_type: str, data_name: str):
    for st in ALL_STAGES:
        _ensure_leaf(store, run_type, data_name, st)

# --- snapshot helpers ---
def _zero_leaf(leaf: dict):
    for k in JOB_STATUS_ORDER:
        leaf[k] = 0

def reset_jobs(store: dict):
    """Clear all jobs but keep logs and metadata."""
    store["jobs"] = {}
    store.setdefault("logs", []).append({
        "ts": utc_now_iso(),
        "level": "INFO",
        "msg": "[SNAPSHOT] reset jobs"
    })

def apply_snapshot(store: dict, leaves: List[dict]):
    """
    Replace the entire jobs tree with the given snapshot.

    Snapshot item formats supported (mix allowed):
      A) {run_type, data_name, stage, counts: {status -> int}, errors?: [...]}
      B) {run_type, data_name, stage, status, count, errors?: [...]}
    """
    reset_jobs(store)

    jobs = store.setdefault("jobs", {})
    for item in leaves or []:
        rt  = (item.get("run_type") or "live").lower()
        dn  = item.get("data_name") or "unknown_data"
        st  = (item.get("stage") or "stage").lower()
        cnt = item.get("counts")
        status = (item.get("status") or "").lower()
        count  = int(item.get("count", 0) or 0)
        errs   = item.get("errors", [])

        _ensure_all_stages(store, rt, dn)
        leaf = _ensure_leaf(store, rt, dn, st)

        _zero_leaf(leaf)
        if isinstance(cnt, dict):
            for k in JOB_STATUS_ORDER:
                leaf[k] = int(cnt.get(k, 0) or 0)
        elif status in JOB_STATUS_ORDER:
            leaf[status] = max(0, count)

        if errs:
            leaf["errors"] = [
                {"ts": e.get("ts", utc_now_iso()), "msg": str(e.get("msg", ""))}
                for e in errs
            ][:50]

# --- classic incremental ingest (kept) ---
def ingest_job_event(store, payload: dict):
    """
    Body:
      run_type: 'live' | 'backfill'
      data_name: str
      stage: 'stage' | 'archive' | 'enrich'
      status: 'wait'|'retry'|'running'|'failed'|'overdue'|'succeeded'
      count: int (default 1)
      mode: 'inc' (default) | 'set' (set this leaf to exactly 'count' for that status)
      error_info: optional str
    """
    run_type  = (payload.get("run_type") or "live").lower()
    data_name = payload.get("data_name") or "unknown_data"
    stage     = (payload.get("stage") or "stage").lower()
    status    = (payload.get("status") or "wait").lower()
    mode      = (payload.get("mode") or "inc").lower()
    count     = payload.get("count", 1)
    try: count = int(count)
    except Exception: count = 1
    if status not in JOB_STATUS_ORDER: status = "wait"

    _ensure_all_stages(store, run_type, data_name)

    leaf = _ensure_leaf(store, run_type, data_name, stage)
    if mode == "set":
        _zero_leaf(leaf)
        leaf[status] = max(0, count)
    else:
        leaf[status] = int(leaf.get(status, 0)) + count

    err = payload.get("error_info")
    if err:
        leaf["errors"].append({"ts": utc_now_iso(), "msg": str(err)})
        if len(leaf["errors"]) > 50: leaf["errors"] = leaf["errors"][-50:]
    store.setdefault("logs", []).append({
        "ts": utc_now_iso(),
        "level": "ERROR" if status in ("failed","overdue") else "INFO",
        "msg": f"[JOB] {run_type}/{data_name}/{stage} -> {status} ({mode}={count})" + (f" err={err}" if err else "")
    })

# ---------- Aggregation ----------
def sum_counts(leaves: List[Dict]) -> Tuple[Dict, List[Dict]]:
    agg = {k:0 for k in JOB_STATUS_ORDER}; errors=[]
    for leaf in leaves:
        for k in JOB_STATUS_ORDER: agg[k]+= int(leaf.get(k,0) or 0)
        errors.extend(leaf.get("errors", []))
    return agg, errors

def totals_for_run_type(store: dict, run_type: str) -> Dict[str, int]:
    jobs = store.get("jobs", {})
    tot = {k:0 for k in JOB_STATUS_ORDER}
    rt_map = jobs.get(run_type, {})
    for stage_map in rt_map.values():
        for leaf in stage_map.values():
            for k in JOB_STATUS_ORDER: tot[k]+= int(leaf.get(k,0) or 0)
    return tot

def all_status_totals(store: dict) -> Dict[str, int]:
    jobs = store.get("jobs", {})
    tot = {k:0 for k in JOB_STATUS_ORDER}
    for dn_map in jobs.values():
        for stage_map in dn_map.values():
            for leaf in stage_map.values():
                for k in JOB_STATUS_ORDER: tot[k]+= int(leaf.get(k,0) or 0)
    return tot

# ---------- Styles / helpers ----------
def _shade_cell(status: str, value: int, max_value: int):
    if (value or 0) == 0:
        return {"backgroundColor": "#FFFFFF", "color": "#FFFFFF",
                "textAlign":"right","padding":"6px 10px","fontWeight":"600","border":"1px solid #eee",
                "minWidth":"80px","whiteSpace":"nowrap"}
    r,g,b = JOB_RGB[status]
    alpha = 0.15 + 0.75*max(0,min(1,(value or 0)/float(max_value or 1)))
    return {"backgroundColor": f"rgba({r},{g},{b},{alpha:.3f})",
            "textAlign":"right","padding":"6px 10px","fontWeight":"600","border":"1px solid #eee",
            "minWidth":"80px","whiteSpace":"nowrap","color":"#111"}

COL_WIDTHS = {"scope":"34%","each":"9%","err":"12%"}

def header_row():
    return html.Tr([
        html.Th("Scope", style={"textAlign":"left","padding":"6px 10px","width":COL_WIDTHS["scope"]}),
        *[html.Th(s.title(), style={"textAlign":"right","padding":"6px 10px","width":COL_WIDTHS["each"]})
          for s in JOB_STATUS_ORDER],
        html.Th("Error Info", style={"textAlign":"left","padding":"6px 10px","width":COL_WIDTHS["err"]})
    ])

def row_counts(scope_cell, counts: Dict, errors: List[Dict], bold=False):
    maxv = max([counts.get(k,0) for k in JOB_STATUS_ORDER] + [0])
    style_scope = {"textAlign":"left","padding":"6px 10px","width":COL_WIDTHS["scope"]}
    if bold: style_scope["fontWeight"]="700"
    tds = [html.Td(scope_cell, style=style_scope)]
    for k in JOB_STATUS_ORDER:
        v = int(counts.get(k,0) or 0)
        tds.append(html.Td(str(v), style=_shade_cell(k, v, maxv), title=f"{k}: {v}"))
    err_text = "—"
    if errors:
        last = errors[-1].get("msg","")
        err_text = last if len(last)<140 else last[:137]+"…"
    tds.append(html.Td(err_text, style={"padding":"6px 10px","width":COL_WIDTHS["err"]}))
    return html.Tr(tds)

def details_row(colspan: int, children):
    return html.Tr([
        html.Td(children, colSpan=colspan,
                style={"background":"#fafafa","borderTop":"none","padding":"6px 10px"})
    ])

def toggle_button(is_open: bool, scope_key: str, label: str, indent_px=0, bold=False):
    icon = "▼" if is_open else "▶"
    style_label = {"fontWeight":"700"} if bold else {}
    return html.Div([
        html.Button(icon, id={"type":"toggle","scope":scope_key}, n_clicks=0,
                    style={"marginRight":"8px","border":"none","background":"transparent",
                           "cursor":"pointer","fontSize":"14px","lineHeight":"1","width":"20px","padding":"0"}),
        html.Span(label, style=style_label),
    ], style={"display":"flex","alignItems":"center","paddingLeft":f"{indent_px}px"})

def build_unified_table(store: dict, tree_state: dict) -> dbc.Table:
    """Builds one table with live on top, backfill below."""
    jobs = store.get("jobs", {})
    rts_open = set(tree_state.get("rts", []))
    dns_open_map = tree_state.get("dns", {})
    sts_open_map = tree_state.get("sts", {})

    def rt_order(keys):
        ordered=[]
        if "live" in keys: ordered.append("live")
        if "backfill" in keys: ordered.append("backfill")
        for k in sorted(keys):
            if k not in ("live","backfill"): ordered.append(k)
        return ordered

    body_rows = []
    for run_type in rt_order(list(jobs.keys())):
        dn_map = jobs[run_type]
        for dn in list(dn_map.keys()):
            _ensure_all_stages(store, run_type, dn)

        # run_type aggregate
        leaves = []
        for stage_map in dn_map.values(): leaves.extend(stage_map.values())
        rt_counts, rt_errs = sum_counts(leaves)

        rt_scope = f"rt|{run_type}"
        rt_open = (run_type in rts_open)
        rt_label = toggle_button(rt_open, rt_scope, f"{run_type.title()} (All Data)", indent_px=0, bold=True)
        body_rows.append(row_counts(rt_label, rt_counts, rt_errs, bold=True))

        if rt_open:
            open_dns = set(dns_open_map.get(run_type, []))
            for data_name in sorted(dn_map.keys()):
                stage_map = dn_map[data_name]
                dn_counts, dn_errs = sum_counts([stage_map[s] for s in ALL_STAGES if s in stage_map])

                dn_scope = f"dn|{run_type}|{data_name}"
                dn_open = (data_name in open_dns)
                dn_label = toggle_button(dn_open, dn_scope, f"{run_type.title()} / {data_name} (All Stages)", indent_px=24)
                body_rows.append(row_counts(dn_label, dn_counts, dn_errs))

                if dn_open:
                    open_stages = set(sts_open_map.get(f"{run_type}|{data_name}", []))
                    for stage in ALL_STAGES:
                        leaf = stage_map.get(stage, {**{k:0 for k in JOB_STATUS_ORDER}, "errors":[]})
                        st_scope = f"st|{run_type}|{data_name}|{stage}"
                        st_open = (stage in open_stages)
                        st_label = toggle_button(st_open, st_scope, f"{run_type.title()} / {data_name} / {stage.title()}",
                                                 indent_px=48)
                        body_rows.append(row_counts(st_label, leaf, leaf.get("errors", [])))
                        if st_open:
                            errs = leaf.get("errors", [])[-5:]
                            detail_list = (html.Ul([html.Li(f"{e.get('ts','')} — {e.get('msg','')}") for e in errs], style={"margin":"0"})
                                           if errs else html.I("No recent errors."))
                            body_rows.append(details_row(1 + len(JOB_STATUS_ORDER) + 1, detail_list))

    return dbc.Table(
        [html.Thead(header_row()), html.Tbody(body_rows)],
        bordered=True, hover=False, size="sm", className="mb-3",
        style={"tableLayout":"fixed","width":"100%"}
    )

# ---------- Demo seed ----------
def seed_jobs(store):
    dataset_events = [
        ("live","prices",  [("stage","running",5), ("archive","wait",5), ("enrich","wait",5)]),
        ("live","alpha",   [("stage","overdue",2), ("archive","wait",1), ("enrich","wait",1)]),
        ("backfill","alpha",[("stage","retry",2), ("archive","wait",3), ("enrich","failed",1)]),
        ("live","beta",    [("stage","wait",9), ("archive","wait",1), ("enrich","succeeded",12)]),
    ]
    for rt, dn, triplets in dataset_events:
        _ensure_all_stages(store, rt, dn)
        for st, status, count in triplets:
            if count>0:
                ingest_job_event(store, {"run_type":rt,"data_name":dn,"stage":st,"status":status,"count":count})
        for st in ALL_STAGES:
            _ensure_leaf(store, rt, dn, st)

# ---------- Build the app ----------
external_styles = [dbc.themes.FLATLY]
app = Dash(__name__, external_stylesheets=external_styles, title=APP_TITLE)
server = app.server

# ----------- Routes -----------
@server.post("/ingest_job_event")
def route_ingest_job_event():
    """
    Accepts object or array of events.
    Optional "reset" flag:
      - query param ?reset=1
      - or control record {"__reset__": true} (ignored inside arrays besides the reset)
    """
    try:
        payload = request.get_json(force=True, silent=False)
        reset_flag = request.args.get("reset", "0") == "1"
        store = load_store()

        if isinstance(payload, dict) and payload.get("__reset__"):
            reset_flag = True
        if reset_flag:
            reset_jobs(store)

        if isinstance(payload, list):
            for p in payload:
                if isinstance(p, dict) and p.get("__reset__"):
                    continue
                ingest_job_event(store, p)
        elif isinstance(payload, dict):
            ingest_job_event(store, payload)
        else:
            return jsonify({"ok": False, "error": "Payload must be object or array"}), 400

        save_store(store)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@server.post("/ingest_snapshot")
def route_ingest_snapshot():
    """
    Accepts:
      - { "snapshot": [ ...items... ] }
      - or just [ ...items... ]

    Each snapshot item:
      A) {run_type, data_name, stage, counts: {status->int}, errors?: [...]}
      B) {run_type, data_name, stage, status, count, errors?: [...]}
    """
    try:
        body = request.get_json(force=True, silent=False)
        if isinstance(body, dict) and "snapshot" in body:
            leaves = body["snapshot"]
        elif isinstance(body, list):
            leaves = body
        else:
            return jsonify({"ok": False, "error": "Send {snapshot:[...]} or a JSON array."}), 400

        store = load_store()
        apply_snapshot(store, leaves)
        save_store(store)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@server.post("/store/reset")
def route_reset():
    # Optional seeding via query flag ONLY.
    seed = request.args.get("seed", "0") == "1"
    store = _init_store()
    if seed:
        seed_jobs(store)
    save_store(store)
    return jsonify({"ok": True, "seeded": seed})

# ---------- Layout ----------
app.layout = dbc.Container([
    dcc.Store(id="tree-state", storage_type="session"),
    html.Div(style={"height":"10px"}),
    dbc.Row([
        dbc.Col(html.H2(APP_TITLE, className="fw-bold"), md=8),
        dbc.Col(html.Div(id="now-indicator", className="text-end text-muted"), md=4),
    ], align="center"),

    html.Hr(),

    # KPI row (buttons act like hyperlinks)
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div("Wait", className="text-muted small"),
            html.Button(id="kpi-wait", className="btn btn-link p-0 fw-bold",
                        children="0", style={"textDecoration":"underline"})
        ])]), md=2),
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div("Retry", className="text-muted small"),
            html.Button(id="kpi-retry", className="btn btn-link p-0 fw-bold",
                        children="0", style={"textDecoration":"underline"})
        ])]), md=2),
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div("Running", className="text-muted small"),
            html.Button(id="kpi-running", className="btn btn-link p-0 fw-bold",
                        children="0", style={"textDecoration":"underline"})
        ])]), md=2),
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div("Failed", className="text-muted small"),
            html.Button(id="kpi-failed", className="btn btn-link p-0 fw-bold",
                        children="0", style={"textDecoration":"underline"})
        ])]), md=2),
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div("Overdue", className="text-muted small"),
            html.Button(id="kpi-overdue", className="btn btn-link p-0 fw-bold",
                        children="0", style={"textDecoration":"underline"})
        ])]), md=2),
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div("Succeeded", className="text-muted small"),
            html.Button(id="kpi-succeeded", className="btn btn-link p-0 fw-bold",
                        children="0", style={"textDecoration":"underline"})
        ])]), md=2),
    ], className="gy-3"),

    html.Div(style={"height":"10px"}),

    # Two pies: Live and Backfill
    dbc.Row([
        dbc.Col([dcc.Graph(id="status-pie-live", style={"height":"420px"})], md=6),
        dbc.Col([dcc.Graph(id="status-pie-backfill", style={"height":"420px"})], md=6),
    ], style={"maxWidth":"1400px", "margin":"0"}),

    html.Hr(),

    dbc.Row([
        dbc.Col(html.H4("Jobs — Live (top) and Backfill (bottom)", className="fw-semibold"), md=9),
        dbc.Col(dbc.Button("Collapse all", id="collapse-all", color="secondary", outline=True, size="sm",
                           className="float-end"), md=3)
    ]),
    html.Small("Click ▶ to expand/collapse. KPIs and pie slices open only relevant rows.",
               className="text-muted d-block mb-2"),

    html.Div(id="table-unified", style={"maxWidth":"1400px"}),

    dcc.Interval(id="interval", interval=REFRESH_MS, n_intervals=0),
], fluid=True, className="pt-3 pb-4", style={"maxWidth":"1400px"})

# ---------- Toggle/KPI/Pie/Reset → update tree-state ----------
@app.callback(
    Output("tree-state", "data"),
    # Row toggles
    Input({"type": "toggle", "scope": ALL}, "n_clicks"),
    State({"type": "toggle", "scope": ALL}, "id"),
    State({"type": "toggle", "scope": ALL}, "n_clicks"),  # <-- add this
    # KPI “links”
    Input("kpi-wait", "n_clicks"),
    Input("kpi-retry", "n_clicks"),
    Input("kpi-running", "n_clicks"),
    Input("kpi-failed", "n_clicks"),
    Input("kpi-overdue", "n_clicks"),
    Input("kpi-succeeded", "n_clicks"),
    # Pie clicks
    Input("status-pie-live", "clickData"),
    Input("status-pie-backfill", "clickData"),
    # Reset button
    Input("collapse-all", "n_clicks"),
    State("tree-state", "data"),
    prevent_initial_call=True,
)
def update_tree_state(_toggle_clicks, _toggle_ids, _toggle_values,   # <-- new arg
                      k_wait, k_retry, k_running, k_failed, k_overdue, k_succeeded,
                      pie_live_click, pie_backfill_click,
                      collapse_click,
                      state):
    state = state or {"rts": [], "dns": {}, "sts": {}}
    trig = ctx.triggered_id

    ...
    # Row toggle button
    if isinstance(trig, dict) and trig.get("type") == "toggle":
        # find the triggered toggle's current click count
        clicks = 0
        if _toggle_ids and _toggle_values:
            for i, tid in enumerate(_toggle_ids):
                if tid == trig:
                    clicks = _toggle_values[i] or 0
                    break
        # Ignore spurious fires (e.g., components created with n_clicks == 0)
        if clicks <= 0:
            return state

        scope = trig.get("scope", "")
        parts = scope.split("|")
        if parts[0] == "rt":
            rt = parts[1]
            rts = set(state.get("rts", []))
            rts.remove(rt) if rt in rts else rts.add(rt)
            state["rts"] = sorted(rts, key=lambda x: {"live":0,"backfill":1}.get(x,2))
        elif parts[0] == "dn":
            rt, dn = parts[1], parts[2]
            dns = state.setdefault("dns", {})
            lst = set(dns.get(rt, []))
            lst.remove(dn) if dn in lst else lst.add(dn)
            dns[rt] = sorted(lst)
        elif parts[0] == "st":
            rt, dn, st = parts[1], parts[2], parts[3]
            sts = state.setdefault("sts", {})
            key = f"{rt}|{dn}"
            lst = set(sts.get(key, []))
            lst.remove(st) if st in lst else lst.add(st)
            sts[key] = sorted(lst)
        return state

    # KPI clicks: collapse-all, then open only items with that status > 0 (across run types)
    kpi_to_status = {
        "kpi-wait": "wait",
        "kpi-retry": "retry",
        "kpi-running": "running",
        "kpi-failed": "failed",
        "kpi-overdue": "overdue",
        "kpi-succeeded": "succeeded",
    }
    if trig in kpi_to_status:
        want = kpi_to_status[trig]
        store = load_store()
        jobs = store.get("jobs", {})
        new_state = {"rts": [], "dns": {}, "sts": {}}
        for rt, dn_map in jobs.items():
            rt_has = False
            dn_list = []
            st_map = {}
            for dn, stage_map in dn_map.items():
                st_list = [st for st, leaf in stage_map.items() if int(leaf.get(want, 0) or 0) > 0]
                if st_list:
                    rt_has = True
                    dn_list.append(dn)
                    st_map[f"{rt}|{dn}"] = sorted(st_list)
            if rt_has:
                new_state["rts"].append(rt)
                if dn_list:
                    new_state["dns"][rt] = sorted(dn_list)
                if st_map:
                    new_state["sts"].update(st_map)
        new_state["rts"] = sorted(set(new_state["rts"]), key=lambda x: {"live":0,"backfill":1}.get(x,2))
        return new_state

    # Pie clicks: collapse-all, then open rows for that RUN TYPE **and** the CLICKED STATUS
    if trig in ("status-pie-live", "status-pie-backfill"):
        click = pie_live_click if trig == "status-pie-live" else pie_backfill_click
        if not click or "points" not in click or not click["points"]:
            return state
        label = click["points"][0].get("label")
        want = _label_to_status(label)
        run_type = "live" if trig == "status-pie-live" else "backfill"

        store = load_store()
        jobs = store.get("jobs", {})
        dn_map = jobs.get(run_type, {})

        new_state = {"rts": [], "dns": {}, "sts": {}}
        dn_list = []
        st_map = {}
        for dn, stage_map in dn_map.items():
            st_list = [st for st, leaf in stage_map.items() if want and int(leaf.get(want, 0) or 0) > 0]
            if st_list:
                dn_list.append(dn)
                st_map[f"{run_type}|{dn}"] = sorted(st_list)
        new_state["rts"] = [run_type]
        if dn_list:
            new_state["dns"][run_type] = sorted(dn_list)
            new_state["sts"] = st_map
        return new_state

    return state

# ---------- Main refresh ----------
@app.callback(
    Output("kpi-wait","children"),
    Output("kpi-retry","children"),
    Output("kpi-running","children"),
    Output("kpi-failed","children"),
    Output("kpi-overdue","children"),
    Output("kpi-succeeded","children"),
    Output("status-pie-live","figure"),
    Output("status-pie-backfill","figure"),
    Output("table-unified","children"),
    Output("now-indicator","children"),
    Output("interval","interval"),
    Input("interval","n_intervals"),
    Input("tree-state","data"),
    State("interval","interval"),
)
def refresh(_n, tree_state, cur_interval):
    interval_ms = int(cur_interval or REFRESH_MS)
    store = load_store()
    # if MOCK_MODE and not store.get("jobs"):
    #     seed_jobs(store); save_store(store)

    totals = all_status_totals(store)
    wait = totals["wait"]; retry = totals["retry"]; running = totals["running"]
    failed = totals["failed"]; overdue = totals["overdue"]; succeeded = totals["succeeded"]

    live_tot  = totals_for_run_type(store, "live")
    back_tot  = totals_for_run_type(store, "backfill")

    def _pie(title, tot):
        labels = [s.title() for s in JOB_STATUS_ORDER]
        values = [tot.get(s, 0) for s in JOB_STATUS_ORDER]
        colors = [JOB_COLORS[s] for s in JOB_STATUS_ORDER]
        return {"data":[{"type":"pie","labels":labels,"values":values,"hole":0.45,
                         "marker":{"colors":colors},
                         "hovertemplate":"%{label}: %{value}<extra></extra>"}],
                "layout":{"title":title,"height":420, "margin":{"l":20,"r":20,"t":50,"b":20}}}

    fig_live = _pie("Status Mix — Live", live_tot)
    fig_back = _pie("Status Mix — Backfill", back_tot)

    tree_state = tree_state or {"rts": [], "dns": {}, "sts": {}}
    table = build_unified_table(store, tree_state)

    now_local = datetime.now(_DEF_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    return (str(wait), str(retry), str(running), str(failed), str(overdue), str(succeeded),
            fig_live, fig_back, table, f"Refreshed: {now_local}", interval_ms)

# ---------- Run ----------
if __name__ == "__main__":
    # No automatic seeding. If you want a dev toggle, set DEMO_SEED_ON_START=1.
    if os.getenv("DEMO_SEED_ON_START", "0") == "1":
        s = load_store()
        if not s.get("jobs"):
            seed_jobs(s); save_store(s)
    app.run_server(host="0.0.0.0", port=8050, debug=False)