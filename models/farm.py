from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from models.iot import SensorData
from db.config import db


class FarmCreate(BaseModel):
    name: str
    key: str
    @staticmethod
    def init():
        db.farm.create_index([("key", 1)], unique=True)


class FarmData(SensorData):
    farm_short_id: str
    date_added: datetime

class Farm(FarmCreate):
    short_id: str
    motor_state: Optional[str]