"""
Data Retrieval Monitor — Owner/Mode dashboard (filters; no sorting).

Layout
- Left pane (narrow): Filters → KPIs (2 rows: 4 + 3) → 4 pies (Stage/Archive/Enrich/Consolidate).
- Right pane (wide): Datasets table. If long, auto-splits into 2 side-by-side tables.

Table cells
- Only chunk badges (c0, c1, …) with proc/log links, one single line per cell
  (horizontally scrollable if overflowing). No "Stage: Status" label.

Filters
- Owner (default = DEFAULT_OWNER; includes "All")
- Mode  (default = DEFAULT_MODE; includes "All")
- Stage (multi-select; combined with Status)
- Status (multi-select; combined with Stage)
Table rule:
- Show a dataset if ANY selected stage has a status within the selected statuses.
- If no statuses are selected, the Stage filter is ignored for the table.

Ingestion
- POST /ingest_snapshot  (JSON: {"snapshot":[...]} or just [...]) — REPLACES all state
- POST /feed             (same as /ingest_snapshot; convenience)
- POST /store/reset?seed=1

Environment
- DEFAULT_OWNER (default "QSG")
- DEFAULT_MODE  (default "live")
- REFRESH_MS (default 1000 ms)
- STORE_BACKEND=memory|file (default memory), STORE_PATH=path/to.json (if file)
- APP_TIMEZONE (default Europe/London)
- TABLE_SPLIT_THRESHOLD (default 80)  # rows; if exceeded, table is split into 2 columns
"""

import os, json, tempfile, pathlib, threading
from datetime import datetime, timezone
from typing import Dict, List, Optional

import pytz
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from flask import request, jsonify

# ---------------- Config ----------------
APP_TITLE     = "Data Retrieval Monitor"
TIMEZONE      = os.getenv("APP_TIMEZONE", "Europe/London")
_DEF_TZ       = pytz.timezone(TIMEZONE)
REFRESH_MS    = int(os.getenv("REFRESH_MS", "1000"))
STORE_BACKEND = os.getenv("STORE_BACKEND", "memory")  # memory | file
STORE_PATH    = os.getenv("STORE_PATH", "status_store.json")

DEFAULT_OWNER = os.getenv("DEFAULT_OWNER", "QSG")      # display label & default selection
DEFAULT_MODE  = os.getenv("DEFAULT_MODE",  "live")

TABLE_SPLIT_THRESHOLD = int(os.getenv("TABLE_SPLIT_THRESHOLD", "80"))

# Stages (fixed)
STAGES = ["stage", "archive", "enrich", "consolidate"]

# Statuses (worst → best) — no aliases
JOB_STATUS_ORDER = ["failed", "overdue", "manual", "retrying", "running", "waiting", "succeeded"]
JOB_COLORS = {
    "waiting":   "#F0E442",
    "retrying":  "#E69F00",
    "running":   "#56B4E9",
    "failed":    "#D55E00",
    "overdue":   "#A50E0E",
    "manual":    "#808080",
    "succeeded": "#009E73",
}

def _hex_to_rgb(h): h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
JOB_RGB = {k: _hex_to_rgb(v) for k, v in JOB_COLORS.items()}
def utc_now_iso(): return datetime.now(timezone.utc).isoformat()

# ---------------- Store ----------------
STORE_LOCK = threading.RLock()
_MEM_STORE = None
_STORE_CACHE = None
_STORE_MTIME = None

def _init_store():
    # jobs[owner_key][mode_key][data_name][stage] = {chunks:[], counts:{}, errors:[]}
    # meta.owner_labels maps lowercase owner_key -> first-seen display label
    return {"jobs": {}, "logs": [], "meta": {"owner_labels": {}}, "updated_at": utc_now_iso()}

def ensure_store():
    global _MEM_STORE
    if STORE_BACKEND == "memory":
        if _MEM_STORE is None:
            _MEM_STORE = _init_store()
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
    if len(logs) > 2000:
        store["logs"] = logs[-2000:]
    if STORE_BACKEND == "memory":
        global _MEM_STORE
        with STORE_LOCK:
            _MEM_STORE = store
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
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass

def _ensure_leaf(store, owner: str, mode: str, data_name: str, stage: str) -> Dict:
    jobs = store.setdefault("jobs", {})
    o = jobs.setdefault(owner, {})
    m = o.setdefault(mode, {})
    d = m.setdefault(data_name, {})
    return d.setdefault(stage, {"chunks": [], "counts": {s:0 for s in JOB_STATUS_ORDER}, "errors": []})

def _zero_counts(leaf: Dict):
    leaf["counts"] = {s:0 for s in JOB_STATUS_ORDER}

def _recount_from_chunks(leaf: Dict):
    _zero_counts(leaf)
    for ch in leaf.get("chunks", []):
        st = (ch.get("status") or "waiting").lower()
        if st in leaf["counts"]:
            leaf["counts"][st] += 1

def reset_jobs(store: dict):
    store["jobs"] = {}
    store.setdefault("logs", []).append({"ts": utc_now_iso(), "level":"INFO", "msg":"[SNAPSHOT] reset"})

def apply_snapshot(store: dict, items: List[dict]):
    reset_jobs(store)
    labels = store.setdefault("meta", {}).setdefault("owner_labels", {})

    for it in items or []:
        owner_raw = (it.get("owner") or DEFAULT_OWNER).strip()
        owner_key = owner_raw.lower()
        mode_raw  = (it.get("mode")  or DEFAULT_MODE).strip()
        mode_key  = mode_raw.lower()
        dn        = it.get("data_name") or "unknown"
        stg       = (it.get("stage") or "stage").lower()

        # remember display label once
        labels.setdefault(owner_key, owner_raw)

        leaf = _ensure_leaf(store, owner_key, mode_key, dn, stg)
        if isinstance(it.get("chunks"), list):
            leaf["chunks"] = list(it["chunks"])
        else:
            leaf["chunks"] = []
        leaf["errors"] = list(it.get("errors", []))[-50:] if isinstance(it.get("errors"), list) else []
        _recount_from_chunks(leaf)

# ---------------- Aggregation ----------------
def aggregate_counts(store: dict) -> Dict[str, int]:
    """Global KPIs (not filtered)."""
    tot = {s:0 for s in JOB_STATUS_ORDER}
    for o_map in store.get("jobs", {}).values():
        for m_map in o_map.values():
            for d_map in m_map.values():
                for leaf in d_map.values():
                    for s, v in leaf["counts"].items():
                        tot[s] += int(v or 0)
    return tot

def filtered_stage_counts(store: dict, owner: Optional[str], mode: Optional[str], stage: str) -> Dict[str,int]:
    owner_sel = (owner or "").lower()
    mode_sel  = (mode  or "").lower()
    want_owner = None if owner_sel in ("", "all") else owner_sel
    want_mode  = None if mode_sel  in ("", "all") else mode_sel
    tot = {s:0 for s in JOB_STATUS_ORDER}
    for own, o_map in store.get("jobs", {}).items():
        if want_owner and own != want_owner: continue
        for md, m_map in o_map.items():
            if want_mode and md != want_mode: continue
            for d_map in m_map.values():
                leaf = d_map.get(stage)
                if not leaf: continue
                for s, v in leaf["counts"].items():
                    tot[s] += int(v or 0)
    return tot

def list_filters(store: dict):
    jobs   = store.get("jobs", {})
    labels = store.get("meta", {}).get("owner_labels", {})
    owner_keys = set(jobs.keys()) | {DEFAULT_OWNER.lower()}
    owners = sorted(owner_keys)
    owner_opts = [{"label": "All", "value": "All"}]
    for k in owners:
        owner_opts.append({"label": labels.get(k, k), "value": k})

    # modes (keys lowercase; labels title-cased)
    modes_keys = set()
    for o_map in jobs.values():
        modes_keys.update(o_map.keys())
    modes_keys |= {"live", "backfill", DEFAULT_MODE.lower()}
    modes = sorted(modes_keys)
    mode_opts = [{"label": "All", "value": "All"}] + [{"label": m.title(), "value": m} for m in modes]
    return owner_opts, mode_opts

def best_status(counts: Dict[str,int]) -> Optional[str]:
    for s in JOB_STATUS_ORDER:  # worst→best
        if int(counts.get(s, 0) or 0) > 0:
            return s
    return None

# ---------------- UI helpers ----------------
def shade_for_status(status: Optional[str], alpha=0.22):
    if not status: return {"backgroundColor":"#FFFFFF"}
    r,g,b = JOB_RGB[status]
    return {"backgroundColor": f"rgba({r},{g},{b},{alpha})"}

def chunk_line(chunks: List[dict]):
    """
    Single-line chunk list; horizontally scrollable if long.
    Each chunk shows a colored badge + optional proc/log links.
    """
    if not chunks:
        return html.I("—", className="text-muted")

    nodes = []
    for idx, ch in enumerate(chunks):
        cid  = ch.get("id") or f"c{idx}"
        st   = (ch.get("status") or "waiting").lower()
        proc = ch.get("proc"); log = ch.get("log")

        badge = html.Span(
            cid,
            style={
                "display":"inline-block","padding":"2px 6px","borderRadius":"8px",
                "fontSize":"12px","marginRight":"6px",
                **shade_for_status(st, 0.35)
            }
        )
        nodes.append(badge)
        if proc:
            nodes.append(html.A("proc", href=proc, target="_blank", style={"marginRight":"6px"}))
        if log:
            nodes.append(html.A("log", href=log, target="_blank", style={"marginRight":"10px"}))
        # small spacer between chunks
        nodes.append(html.Span(" ", style={"marginRight":"6px"}))

    return html.Div(
        nodes,
        style={
            "whiteSpace": "nowrap",
            "overflowX": "auto",
            "paddingBottom": "2px"
        }
    )

def build_table_rows(store: dict, owner: Optional[str], mode: Optional[str],
                     stage_filter: List[str], status_filter: List[str]) -> List[html.Tr]:
    owner_sel = (owner or "").lower()
    mode_sel  = (mode  or "").lower()
    want_owner = None if owner_sel in ("", "all") else owner_sel
    want_mode  = None if mode_sel  in ("", "all") else mode_sel

    sel_stages = [s for s in (stage_filter or []) if s in STAGES]
    if not sel_stages:  # empty => treat as all stages selected
        sel_stages = STAGES[:]
    sel_status = [s for s in (status_filter or []) if s in JOB_STATUS_ORDER]
    filter_by_status = len(sel_status) > 0

    rows = []
    for own in sorted(store.get("jobs", {}).keys()):
        if want_owner and own != want_owner: continue
        o_map = store["jobs"][own]
        for md in sorted(o_map.keys()):
            if want_mode and md != want_mode: continue
            m_map = o_map[md]
            for dn in sorted(m_map.keys()):
                d_map = m_map[dn]
                # compute stage best-status map
                stage_status = {}
                for stg in STAGES:
                    leaf = d_map.get(stg, {"counts":{s:0 for s in JOB_STATUS_ORDER}, "chunks":[]})
                    stage_status[stg] = best_status(leaf["counts"])

                # apply Stage+Status filter
                if filter_by_status:
                    if not any((stage_status.get(stg) in sel_status) for stg in sel_stages):
                        continue

                # assemble row
                labels = store.get("meta", {}).get("owner_labels", {})
                owner_label = labels.get(own, own)
                title = f"{owner_label} / {dn}" if not want_owner else dn

                cells = [html.Td(title, style={"fontWeight":"600","whiteSpace":"nowrap"})]
                for stg in STAGES:
                    leaf = d_map.get(stg, {"counts":{s:0 for s in JOB_STATUS_ORDER}, "chunks":[]})
                    status = stage_status[stg]
                    style = {"verticalAlign":"top","padding":"6px 10px", **shade_for_status(status, 0.18)}
                    cells.append(html.Td(chunk_line(leaf.get("chunks", [])), style=style))
                rows.append(html.Tr(cells))
    return rows

def build_table_component(rows: List[html.Tr]) -> dbc.Table:
    head = html.Thead(html.Tr([
        html.Th("Dataset", style={"width":"22%","whiteSpace":"nowrap"}),
        html.Th("Stage"), html.Th("Archive"), html.Th("Enrich"), html.Th("Consolidate")
    ]))
    body = html.Tbody(rows or [html.Tr(html.Td("No data", colSpan=5, className="text-muted"))])
    return dbc.Table([head, body], bordered=True, hover=False, size="sm",
                     className="mb-3", style={"tableLayout":"fixed","width":"100%"})

def pie_figure(title: str, counts: Dict[str,int]):
    labels = [s.title() for s in JOB_STATUS_ORDER]
    values = [int(counts.get(s,0) or 0) for s in JOB_STATUS_ORDER]
    colors = []
    texttempl = []
    for s, v in zip(JOB_STATUS_ORDER, values):
        r,g,b = JOB_RGB[s]
        colors.append(f"rgba({r},{g},{b},{0.85 if v>0 else 0.0})")      # transparent wedge if zero
        texttempl.append("" if v==0 else "%{label} %{percent}")         # hide label for zero

    return {
        "data": [{
            "type": "pie",
            "labels": labels,
            "values": values,
            "hole": 0.45,
            "marker": {"colors": colors, "line": {"width": 0}},
            "texttemplate": texttempl,
            "textposition": "outside",
            "hovertemplate": "%{label}: %{value}<extra></extra>",
            "showlegend": True
        }],
        "layout": {
            "title": {"text": title, "x": 0.5, "xanchor": "center", "y": 0.98},
            "height": 320,
            "margin": {"l": 10, "r": 10, "t": 70, "b": 10},
            "legend": {"orientation": "h"}
        }
    }

# ---------------- App + Routes ----------------
external_styles = [dbc.themes.FLATLY]
app = Dash(__name__, external_stylesheets=external_styles, title=APP_TITLE)
server = app.server

@server.post("/ingest_snapshot")
def route_ingest_snapshot():
    try:
        body = request.get_json(force=True, silent=False)
        items = body["snapshot"] if isinstance(body, dict) and "snapshot" in body else body
        if not isinstance(items, list):
            return jsonify({"ok": False, "error": "Send {snapshot:[...]} or a JSON array."}), 400
        store = load_store()
        apply_snapshot(store, items)
        save_store(store)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@server.post("/feed")
def route_feed():
    return route_ingest_snapshot()

@server.post("/store/reset")
def route_reset():
    seed = request.args.get("seed", "0") == "1"
    store = _init_store()
    if seed:
        _ = _ensure_leaf(store, DEFAULT_OWNER.lower(), DEFAULT_MODE.lower(), "dataset-000", "stage")
    save_store(store)
    return jsonify({"ok": True, "seeded": seed})

# ---------------- Controls (left pane) ----------------
controls_card = dbc.Card(dbc.CardBody([
    html.Div("Owner", className="text-muted small"),
    dcc.Dropdown(
        id="owner-filter",
        options=[{"label":"All", "value":"All"},
                 {"label": DEFAULT_OWNER, "value": DEFAULT_OWNER.lower()}],
        value=DEFAULT_OWNER.lower(),
        clearable=False,
        className="mb-2",
        style={"minWidth":"180px"},
    ),

    html.Div("Mode", className="text-muted small"),
    dcc.Dropdown(
        id="mode-filter",
        options=[{"label":"All", "value":"All"},
                 {"label":"Live", "value":"live"},
                 {"label":"Backfill", "value":"backfill"}],
        value=DEFAULT_MODE.lower(),
        clearable=False,
        style={"minWidth":"180px"},
        className="mb-2",
    ),

    html.Div("Stage filter (ANY of)", className="text-muted small"),
    dcc.Dropdown(
        id="stage-filter",
        options=[{"label": s.title(), "value": s} for s in STAGES],
        value=STAGES,  # default: all selected; harmless when status filter is empty
        multi=True,
        className="mb-2",
    ),

    html.Div("Status filter (ANY of)", className="text-muted small"),
    dcc.Dropdown(
        id="status-filter",
        options=[{"label": s.title(), "value": s} for s in JOB_STATUS_ORDER],
        value=[],
        multi=True,
        placeholder="(none)",
    ),
]))

# KPIs in two rows: 4 then 3
kpi_row_top = dbc.Row([
    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Waiting", className="text-muted small"),
                                   html.H4(id="kpi-waiting", className="mb-0")])), md=3),
    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Retrying", className="text-muted small"),
                                   html.H4(id="kpi-retrying", className="mb-0")])), md=3),
    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Running", className="text-muted small"),
                                   html.H4(id="kpi-running", className="mb-0")])), md=3),
    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Failed", className="text-muted small"),
                                   html.H4(id="kpi-failed", className="mb-0")])), md=3),
], className="gy-2")

kpi_row_bottom = dbc.Row([
    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Overdue", className="text-muted small"),
                                   html.H4(id="kpi-overdue", className="mb-0")])), md=4),
    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Manual", className="text-muted small"),
                                   html.H4(id="kpi-manual", className="mb-0")])), md=4),
    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Succeeded", className="text-muted small"),
                                   html.H4(id="kpi-succeeded", className="mb-0")])), md=4),
], className="gy-2")

pies_block = html.Div([
    dbc.Row([
        dbc.Col(dcc.Graph(id="pie-stage",        style={"height":"320px"}), md=12),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="pie-archive",      style={"height":"320px"}), md=12),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="pie-enrich",       style={"height":"320px"}), md=12),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="pie-consolidate",  style={"height":"320px"}), md=12),
    ]),
], className="mb-2")

# ---------------- Page layout: Left controls & charts, Right table ----------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2(APP_TITLE, className="fw-bold"), md=8),
        dbc.Col(html.Div(id="now-indicator", className="text-end text-muted"), md=4),
    ], align="center"),

    dbc.Row([
        # Left narrow pane
        dbc.Col([
            controls_card,
            html.Div(style={"height":"10px"}),
            kpi_row_top,
            html.Div(style={"height":"8px"}),
            kpi_row_bottom,
            html.Div(style={"height":"10px"}),
            pies_block
        ], md=3, lg=3, xl=3, xxl=3),

        # Right wide pane (tables)
        dbc.Col([
            html.H4("Datasets", className="fw-semibold"),
            html.Div(id="table-container", style={"maxWidth":"100%", "overflowX":"auto"}),
        ], md=9, lg=9, xl=9, xxl=9),
    ], align="start", className="mt-2"),

    dcc.Interval(id="interval", interval=REFRESH_MS, n_intervals=0)
], fluid=True, className="pt-3 pb-4")

# ---------------- Callback ----------------
@app.callback(
    Output("kpi-waiting","children"),
    Output("kpi-retrying","children"),
    Output("kpi-running","children"),
    Output("kpi-failed","children"),
    Output("kpi-overdue","children"),
    Output("kpi-manual","children"),
    Output("kpi-succeeded","children"),
    Output("owner-filter","options"),
    Output("mode-filter","options"),
    Output("pie-stage","figure"),
    Output("pie-archive","figure"),
    Output("pie-enrich","figure"),
    Output("pie-consolidate","figure"),
    Output("table-container","children"),
    Output("now-indicator","children"),
    Output("interval","interval"),
    Input("interval","n_intervals"),
    Input("owner-filter","value"),
    Input("mode-filter","value"),
    Input("stage-filter","value"),
    Input("status-filter","value"),
    State("interval","interval"),
)
def refresh(_n, owner_sel, mode_sel, stage_filter, status_filter, cur_interval):
    interval_ms = int(cur_interval or REFRESH_MS)
    store = load_store()

    # KPIs (global)
    k = aggregate_counts(store)
    kpi_vals = [str(k[s]) for s in ["waiting","retrying","running","failed","overdue","manual","succeeded"]]

    # Filters options from data (always includes "All", defaults)
    owner_opts, mode_opts = list_filters(store)

    # Pies (filtered by owner/mode only) — titles guaranteed visible
    figs = []
    for stg in STAGES:
        c = filtered_stage_counts(store, owner_sel, mode_sel, stg)
        figs.append(pie_figure(stg.title(), c))

    # Table rows (filtered by owner/mode + stage/status combo)
    rows = build_table_rows(store, owner_sel, mode_sel, stage_filter or [], status_filter or [])

    # Auto-split into two tables if many rows
    if len(rows) > TABLE_SPLIT_THRESHOLD:
        mid = len(rows) // 2
        tbl1 = build_table_component(rows[:mid])
        tbl2 = build_table_component(rows[mid:])
        table_comp = dbc.Row([
            dbc.Col(tbl1, md=6),
            dbc.Col(tbl2, md=6),
        ], className="g-3")
    else:
        table_comp = build_table_component(rows)

    now_local = datetime.now(_DEF_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    return (*kpi_vals, owner_opts, mode_opts, *figs, table_comp, f"Refreshed: {now_local}", interval_ms)

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)