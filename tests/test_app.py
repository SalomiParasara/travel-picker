import json
from app import app

def test_healthz_ok():
    client = app.test_client()
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"

def test_api_destination():
    client = app.test_client()
    r = client.get("/api/destination")
    assert r.status_code == 200
    data = r.get_json()
    for key in ["destination", "country", "season", "budget"]:
        assert key in data
