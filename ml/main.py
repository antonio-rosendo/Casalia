from fastapi import FastAPI
from schemas.prediction import PredictionInput, PredictionOutput
from backend_features import run_prediction

app = FastAPI()

@app.post("/predict", response_model=PredictionOutput)
def predict(req: PredictionInput):
    result = run_prediction(req.comunidad_autonoma, req.precio_total, req.metros_cuadrados)
    return result
