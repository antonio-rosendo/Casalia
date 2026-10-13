"""Request and response models of the API.

Changes are fractions (0.05 = +5%) over the 12 months from the origin quarter
to the target quarter.
"""

from pydantic import BaseModel, ConfigDict, Field


class ChampionForecast(BaseModel):
    chg_12m: float
    low: float = Field(description="lower end of the 80% interval")
    high: float = Field(description="upper end of the 80% interval")


class ChallengerForecast(BaseModel):
    chg_12m: float
    explanation: dict[str, float] | None = Field(
        None, description="SHAP contribution of each feature group, relative to the "
                          "model's average forecast")


class RegionForecast(BaseModel):
    region: str
    name: str
    small_market: bool
    price_m2_at_origin: float
    champion: ChampionForecast
    challenger: ChallengerForecast


class ForecastFile(BaseModel):
    """The payload written by publish_forecasts.py."""
    generated_on: str
    origin: str
    target: str
    target_meaning: str
    champion: str
    challenger: str
    interval: str
    challenger_average_forecast: float | None = None
    regions: list[RegionForecast]


class Health(BaseModel):
    status: str
    origin: str
    target: str
    generated_on: str


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    region: str = Field(examples=["madrid"], description="region slug, see GET /forecasts")
    price: float = Field(gt=0, le=100_000_000, description="current price of the home in EUR")
    area_m2: float | None = Field(None, gt=0, le=10_000, description="floor area, optional")


class ChampionPrediction(ChampionForecast):
    model: str
    price: float
    price_low: float
    price_high: float


class ChallengerPrediction(ChallengerForecast):
    model: str
    price: float
    average_forecast: float | None


class PredictResponse(BaseModel):
    region: str
    name: str
    origin: str
    target: str
    champion: ChampionPrediction
    challenger: ChallengerPrediction = Field(
        description="shadow model: shown for comparison, not used for the headline forecast")
    price_m2: float | None = Field(None, description="price per m2 of this home, if area given")
    regional_price_m2: float = Field(description="regional average appraised value per m2 "
                                                 "at the origin quarter (MIVAU)")
    notes: list[str]
