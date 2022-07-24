from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from models.farm import Farm, FarmCreate, FarmData
from models.user import UserInDB
from db.config import db
from utils.utils import generate_short_id
from oauth.auth import get_current_user
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError



farm_route = APIRouter(
    tags=["Farm 🌾"],
    prefix="/api/v1/farm"
)



@farm_route.post('/add')
async def add_farm(data: FarmCreate, user: UserInDB = Depends(get_current_user)):
    farm = {
        "user_id": ObjectId(user.id),
        "name": data.name,
        "key": data.key,
        "short_id": generate_short_id()
    }

    try:
        db.farm.insert_one(farm)
    except DuplicateKeyError:
        return JSONResponse(
            {"message": "Key already exists"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return {"message": "Farm Added"}

@farm_route.get("/all", response_model=List[Farm])
async def all_farms(user: UserInDB = Depends(get_current_user)):
    db_farms = db.farm.find({"user_id": ObjectId(user.id)})
    farms = [Farm(**farm) for farm in db_farms]
    return farms


@farm_route.get("/farm-data/{farm_short_id}", response_model=List[FarmData])
async def farm_data(farm_short_id: str, user: UserInDB = Depends(get_current_user)):
    db_farm_data = db.farmdata.find({"farm_short_id": farm_short_id})
    farm_data = [FarmData(**farm_datum) for farm_datum in db_farm_data]
    return farm_data
