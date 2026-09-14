"""Tiny Flask dashboard:  python dashboard.py   ->  http://localhost:5000"""
from datetime import date
from flask import Flask, jsonify, render_template_string, request
import config
import db

app = Flask(__name__)

PAGE = """<!doctype html><html><head><meta charset=utf-8>
<title>Iron-Watch attendance</title>
<style>body{font-family:system-ui;margin:2rem;background:#f5f6f8}
table{border-collapse:collapse;background:#fff;box-shadow:0 1px 3px #0002}
th,td{padding:.45rem .9rem;border-bottom:1px solid #e4e6ea;text-align:left}
th{background:#1f2937;color:#fff}.IN{color:#059669;font-weight:600}
.OUT{color:#dc2626;font-weight:600}.metal{background:#fef3c7}h2{margin-top:2rem}</style>
<meta http-equiv=refresh content=10></head><body>
<h1>Iron-Watch &mdash; gate attendance</h1>
<form method=get>Day: <input type=date name=day value="{{day}}"><button>Show</button></form>
<h2>Daily summary ({{day}})</h2>
<table><tr><th>ID</th><th>Name</th><th>First IN</th><th>Last OUT</th><th>Hours</th><th>Metal alerts</th></tr>
{% for r in summary %}<tr><td>{{r.emp_id}}</td><td>{{r.name}}</td>
<td>{{(r.first_in or '')[11:]}}</td><td>{{(r.last_out or '')[11:]}}</td>
<td>{{r.hours if r.hours is not none else '-'}}</td><td>{{r.metal_alerts}}</td></tr>{% endfor %}</table>
<h2>Latest events</h2>
<table><tr><th>Time</th><th>ID</th><th>Name</th><th>Event</th><th>Match dist.</th><th>Metal</th></tr>
{% for r in events %}<tr class="{{'metal' if r.metal else ''}}"><td>{{r.ts.replace('T',' ')}}</td>
<td>{{r.emp_id}}</td><td>{{r.name}}</td><td class="{{r.event}}">{{r.event}}</td>
<td>{{r.confidence}}</td><td>{{'YES' if r.metal else ''}}</td></tr>{% endfor %}</table>
<p style="color:#666">Auto-refreshes every 10 s. JSON: <a href=/api/events>/api/events</a>, <a href=/api/summary>/api/summary</a></p>
</body></html>"""


@app.route("/")
def index():
    day = request.args.get("day") or date.today().isoformat()
    return render_template_string(PAGE, day=day, summary=db.daily_summary(day), events=db.recent(50))


@app.route("/api/events")
def api_events():
    return jsonify(db.recent(int(request.args.get("limit", 200))))


@app.route("/api/summary")
def api_summary():
    return jsonify(db.daily_summary(request.args.get("day") or date.today().isoformat()))


if __name__ == "__main__":
    app.run(host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT, debug=False)
