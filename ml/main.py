from fastapi import FastAPI
from pydantic import BaseModel
from backend_features import run_prediction

app = FastAPI()


class PredictRequest(BaseModel):
    comunidad_id: str
    year: int
    month: int
    precio_actual_vivienda: float
    metros_cuadrados: float


@app.post("/predict")
def predict(req: PredictRequest):
    result = run_prediction(req.dict())
    return result