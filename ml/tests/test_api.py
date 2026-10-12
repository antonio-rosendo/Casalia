"""Smoke tests of the API against the published forecasts."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_predict_applies_the_forecast_to_the_price():
    r = client.post("/predict", json={"region": "Madrid", "price": 200_000, "area_m2": 80})
    assert r.status_code == 200
    body = r.json()
    champ = body["champion"]
    assert champ["price"] == pytest.approx(200_000 * (1 + champ["chg_12m"]), abs=0.01)
    assert champ["price_low"] <= champ["price"] <= champ["price_high"]
    assert body["price_m2"] == 2500.0
    assert set(body["challenger"]["explanation"]) == {
        "momentum", "inflation", "rates", "labour", "credit"}


def test_small_markets_are_flagged():
    body = client.post("/predict", json={"region": "ceuta", "price": 100_000}).json()
    assert any("Small market" in n for n in body["notes"])


@pytest.mark.parametrize("payload, status", [
    ({"region": "atlantis", "price": 100_000}, 404),
    ({"region": "madrid", "price": 0}, 422),
    ({"region": "madrid", "price": -5}, 422),
    ({"region": "madrid", "price": 100_000, "area_m2": 0}, 422),
    ({"region": "madrid", "price": 100_000, "rooms": 3}, 422),
])
def test_bad_input_is_rejected(payload, status):
    assert client.post("/predict", json=payload).status_code == status


def test_no_forecasts_published(monkeypatch, tmp_path):
    monkeypatch.setenv("CASALIA_FORECASTS", str(tmp_path / "missing.json"))
    assert client.get("/health").status_code == 503
