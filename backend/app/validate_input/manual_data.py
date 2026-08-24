from pydantic import BaseModel
from typing import Optional

# Add this Pydantic model for request validation
class PredictionInput(BaseModel):
    operator_id: Optional[str] = "Unknown"
    Feed_Flowrate_m3h: float
    Feed_TDS_ppm: float
    Feed_Salinity_gL: float
    Feed_Temperature_C: float
    Recovery_percent: float
    Flux_LMH: float
    Pressure_Drop_bar: float