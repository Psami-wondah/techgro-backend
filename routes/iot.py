import json
from typing import Optional
from fastapi import APIRouter, Request
import pymongo
from db.config import db
from models.farm import Farm, FarmData
from models.iot import SensorData
from datetime import datetime
from oauth.auth import get_sio_user
from serializers.serializers import serialize_list
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
    farm_data={
        "date_added": datetime.utcnow(),
        "temperature": data.temperature,
        "humidity": data.humidity,
        "soil_moisture": data.soil_moisture,
        "farm_short_id": farm.short_id

    }
    db.farmdata.insert_one(farm_data)
    c = await request.json()
    await sio.emit("new_sensor_data", farm_data, room=farm.short_id)

    return {"message": "New farm data added", "data": c}

@sio.on("connect")
async def connect(sid, env, auth):
    if auth:
        user = await get_sio_user(auth["token"])
        if user:
            print("SocketIO connect")
            farm_short_id = auth['farm_short_id']
            print(farm_short_id)
            sio.enter_room(sid, str(farm_short_id))
            await sio.emit("connect", f"User {user.username} connected as {sid}")
        else:
            raise ConnectionRefusedError("authentication failed")
    else:
        raise ConnectionRefusedError("no auth token")



@sio.on('sensor_data')
async def print_message(sid, data):
    data = json.loads(data)
    print("received smth")
    farm_short_id = data['farm_short_id']
    db_farm_data = db.farmdata.find({"farm_short_id": farm_short_id}).sort([("date_added", pymongo.DESCENDING)])
    db_farm_data = serialize_list(db_farm_data)
    if not len(db_farm_data) == 0:
        farm_data = FarmData(**db_farm_data[0])
        farm_data.date_added = str(farm_data.date_added)
        farm_data = farm_data.dict()
        print("sending_smth")
        await sio.emit("new_sensor_data", farm_data, room=farm_short_id)


@sio.on("disconnect")
async def disconnect(sid):
    print("SocketIO disconnect")