from fastapi import APIRouter, Request

from models.iot import SensorData

iot = APIRouter(
    tags=["Auth 🔐"],
    prefix="/api/v1/iot"
)



@iot.post('/sensors')
async def sensors_response(data: SensorData, request: Request):
    c = await request.json()
    print(c)
    return c