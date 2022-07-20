from pydantic import BaseModel


class SensorData(BaseModel):
    temp: str