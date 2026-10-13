"""HTTP API over the published forecasts.

It serves the forecasts written by publish_forecasts.py (batch inference): the
models are fitted once a quarter, when the new data come out, not on every
request. The API, the web app and the dated log in forecasts/ therefore show
the same numbers. publish_forecasts.py only forecasts from the latest quarter
that every source has published.

Run from ml/:  uvicorn app.main:app

Settings (environment variables):
  CASALIA_FORECASTS        forecasts JSON to serve (default: ../web/public/forecasts.json)
  CASALIA_ALLOWED_ORIGINS  comma-separated origins allowed by CORS (default: http://localhost:5173)
"""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    ChallengerPrediction,
    ChampionPrediction,
    ForecastFile,
    Health,
    PredictRequest,
    PredictResponse,
    RegionForecast,
)

DEFAULT_FORECASTS = Path(__file__).resolve().parents[2] / "web" / "public" / "forecasts.json"

app = FastAPI(title="Casalia", version="2.0",
              description="12-month forecasts of the appraised price per m2 by Spanish region.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CASALIA_ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def load_forecasts() -> ForecastFile:
    # Read on every request: the file is small and a new quarter needs no restart
    # (the Docker image copies the file in, so rebuild the image instead).
    path = Path(os.environ.get("CASALIA_FORECASTS", DEFAULT_FORECASTS))
    try:
        return ForecastFile.model_validate_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise HTTPException(503, "No forecasts have been published yet") from None


def find_region(forecasts: ForecastFile, region: str) -> RegionForecast:
    slug = region.strip().lower()
    for r in forecasts.regions:
        if r.region == slug:
            return r
    raise HTTPException(404, f"Unknown region '{region}'. See GET /forecasts for the list.")


@app.get("/health", response_model=Health)
def health() -> Health:
    f = load_forecasts()
    return Health(status="ok", origin=f.origin, target=f.target, generated_on=f.generated_on)


@app.get("/forecasts", response_model=ForecastFile)
def forecasts() -> ForecastFile:
    return load_forecasts()


@app.get("/forecasts/{region}", response_model=RegionForecast)
def region_forecast(region: str) -> RegionForecast:
    return find_region(load_forecasts(), region)


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    f = load_forecasts()
    r = find_region(f, req.region)
    champ, chall = r.champion, r.challenger
    notes = [f"Forecast from {f.origin} data to {f.target}. It is the regional average "
             "appraised value applied to this home; it knows nothing about the home itself."]
    if r.small_market:
        notes.append("Small market: few appraisals per quarter, so the data are noisy.")
    return PredictResponse(
        region=r.region, name=r.name, origin=f.origin, target=f.target,
        champion=ChampionPrediction(
            model=f.champion, chg_12m=champ.chg_12m, low=champ.low, high=champ.high,
            price=round(req.price * (1 + champ.chg_12m), 2),
            price_low=round(req.price * (1 + champ.low), 2),
            price_high=round(req.price * (1 + champ.high), 2)),
        challenger=ChallengerPrediction(
            model=f.challenger, chg_12m=chall.chg_12m, explanation=chall.explanation,
            price=round(req.price * (1 + chall.chg_12m), 2),
            average_forecast=f.challenger_average_forecast),
        price_m2=round(req.price / req.area_m2, 1) if req.area_m2 else None,
        regional_price_m2=r.price_m2_at_origin,
        notes=notes,
    )
