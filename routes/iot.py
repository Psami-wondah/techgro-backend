import json
from typing import Optional
from fastapi import APIRouter, Request
import pymongo
from db.config import db
from models.farm import Farm, FarmData
from models.iot import SensorData
from datetime import datetime
from oauth.auth import get_sio_user
from utils import config
import socketio
from typing import Any

iot = APIRouter(
    tags=["Iot 💻"],
    prefix="/api/v1/iot"
)

mgr = socketio.AsyncRedisManager(config.REDIS_URL)
sio: Any = socketio.AsyncServer(async_mode="asgi", client_manager=mgr, cors_allowed_origins="*")


@iot.post('/sensors')
async def sensors_response(data: SensorData, request: Request, key: str):
    db_farm = db.farm.find_one({"key": key})
    farm = Farm(**db_farm)
    db.farmdata.insert_one({
        "date_added": datetime.utcnow(),
        "temperature": data.temperature,
        "humidity": data.humidity,
        "soil_moisture": data.soil_moisture,
        "farm_short_id": farm.short_id

    })
    c = await request.json()
    return {"message": "New farm data added", "data": c}

@sio.on("connect")
async def connect(sid, env, auth):
    if auth:
        user = await get_sio_user(auth["token"])
        if user:
            print("SocketIO connect")
            farm_short_id = auth['farm_short_id']
            sio.enter_room(sid, str(farm_short_id))
            await sio.emit("connect", f"User {user.username} connected as {sid}")
        else:
            raise ConnectionRefusedError("authentication failed")
    else:
        raise ConnectionRefusedError("no auth token")



@sio.on('sensor_data')
async def print_message(sid, data):
    data = json.loads(data)
    farm_short_id = data['farm_short_id']
    db_farm_data = db.farmdata.find({"farm_short_id": farm_short_id}).sort([("date_added", pymongo.DESCENDING)])
    farm_data = FarmData(**db_farm_data[0]).dict()
    await sio.emit("new_sensor_data", farm_data, room=farm_short_id)
