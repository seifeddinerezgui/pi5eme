from pydantic import BaseModel

class VaRResponse(BaseModel):
    VaR: float
    confidence_level: float
