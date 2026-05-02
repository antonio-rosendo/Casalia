from pydantic import BaseModel, Field

class PredictionInput(BaseModel):
    comunidad_autonoma: str = Field(..., description="Nombre de la comunidad autónoma. Ej: 'andalucia', 'madrid'")
    metros_cuadrados: float = Field(..., description="Metros cuadrados de la vivienda")
    precio_total: float = Field(..., description="Precio total actual de la vivienda")

class PredictionOutput(BaseModel):
    pct_change_12m: float = Field(..., description="Variación porcentual predicha a 12 meses (ej: 0.05 significa +5%)")
    precio_actual_vivienda: float = Field(..., description="Precio total actual")
    precio_futuro_vivienda: float = Field(..., description="Precio total predicho a 12 meses")
