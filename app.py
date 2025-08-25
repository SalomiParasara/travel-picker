from __future__ import annotations
import json, os, random
from pathlib import Path
from flask import Flask, request, jsonify, render_template

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "destinations.json"

app = Flask(__name__)

with DATA_FILE.open("r", encoding="utf-8") as f:
    DESTS = json.load(f)["destinations"]

def filter_dests(season=None, budget=None):
    items = DESTS
    if season:
        items = [d for d in items if d["season"].lower() == season.lower()]
    if budget:
        items = [d for d in items if d["budget"].lower() == budget.lower()]
    return items

@app.get("/")
def home():
    season = request.args.get("season")
    budget = request.args.get("budget")
    pool = filter_dests(season, budget) or DESTS
    choice = random.choice(pool)
    return render_template("index.html", d=choice, season=season, budget=budget)

@app.get("/api/destination")
def api_destination():
    season = request.args.get("season")
    budget = request.args.get("budget")
    pool = filter_dests(season, budget) or DESTS
    choice = random.choice(pool)
    return jsonify(choice)

@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
