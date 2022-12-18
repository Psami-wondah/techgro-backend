from pydantic import BaseModel


class SensorData(BaseModel):
    temperature: str
    soil_moisture: str
    humidity: str

class Motor(BaseModel):
    state: str 