"""SQLite storage: workers table + attendance log. Pure stdlib."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS workers (
    emp_id   TEXT PRIMARY KEY,
    name     TEXT NOT NULL,
    label    INTEGER UNIQUE NOT NULL      -- integer label used by LBPH
);
CREATE TABLE IF NOT EXISTS attendance (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id    TEXT NOT NULL,
    name      TEXT NOT NULL,
    event     TEXT NOT NULL CHECK(event IN ('IN','OUT')),
    ts        TEXT NOT NULL,             -- ISO-8601 local time
    confidence REAL,                     -- LBPH distance (lower = better)
    metal     INTEGER DEFAULT 0,         -- 1 if the gate detector was triggered
    FOREIGN KEY(emp_id) REFERENCES workers(emp_id)
);
CREATE INDEX IF NOT EXISTS idx_att_ts ON attendance(ts);
"""


@contextmanager
def connect():
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(config.DB_FILE)
    con.row_factory = sqlite3.Row
    try:
        con.executescript(SCHEMA)
        yield con
        con.commit()
    finally:
        con.close()


def upsert_worker(emp_id: str, name: str, label: int) -> None:
    with connect() as con:
        con.execute(
            "INSERT INTO workers(emp_id,name,label) VALUES(?,?,?) "
            "ON CONFLICT(emp_id) DO UPDATE SET name=excluded.name, label=excluded.label",
            (emp_id, name, label),
        )


def last_event(emp_id: str):
    """Return (event, datetime) of the last log for this worker, or None."""
    with connect() as con:
        row = con.execute(
            "SELECT event, ts FROM attendance WHERE emp_id=? ORDER BY id DESC LIMIT 1",
            (emp_id,),
        ).fetchone()
    return (row["event"], datetime.fromisoformat(row["ts"])) if row else None


def log_event(emp_id: str, name: str, confidence: float, metal: bool) -> str:
    """Toggle IN/OUT for the worker and store it. Returns the event written."""
    prev = last_event(emp_id)
    event = "OUT" if prev and prev[0] == "IN" else "IN"
    with connect() as con:
        con.execute(
            "INSERT INTO attendance(emp_id,name,event,ts,confidence,metal) VALUES(?,?,?,?,?,?)",
            (emp_id, name, event, datetime.now().isoformat(timespec="seconds"),
             round(confidence, 1), int(metal)),
        )
    return event


def recent(limit: int = 200):
    with connect() as con:
        return [dict(r) for r in con.execute(
            "SELECT * FROM attendance ORDER BY id DESC LIMIT ?", (limit,))]


def daily_summary(day: str):
    """Per-worker first IN / last OUT / hours for a YYYY-MM-DD day."""
    with connect() as con:
        rows = con.execute(
            "SELECT emp_id, name, "
            " MIN(CASE WHEN event='IN'  THEN ts END) AS first_in, "
            " MAX(CASE WHEN event='OUT' THEN ts END) AS last_out, "
            " SUM(metal) AS metal_alerts "
            "FROM attendance WHERE substr(ts,1,10)=? GROUP BY emp_id ORDER BY name",
            (day,),
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        if d["first_in"] and d["last_out"]:
            h = (datetime.fromisoformat(d["last_out"]) -
                 datetime.fromisoformat(d["first_in"])).total_seconds() / 3600
            d["hours"] = round(h, 2)
        else:
            d["hours"] = None
        out.append(d)
    return out
