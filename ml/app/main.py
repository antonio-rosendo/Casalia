from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.prediction import PredictionInput, PredictionOutput
from app.services.backend_features import run_prediction

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict", response_model=PredictionOutput)
def predict(req: PredictionInput):
    result = run_prediction(req.comunidad_autonoma, req.precio_total, req.metros_cuadrados)
    return result
