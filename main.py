from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from models.farm import FarmCreate
from models.user import User
from routes.auth import auth
from routes.iot import iot, sio
from routes.farm import farm_route
import socketio

app = FastAPI(
    title="Techgro",
    description="Techgro Apis",
    version="1.0.0",
)

app.include_router(auth)
app.include_router(iot)
app.include_router(farm_route)
socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    User.init()
    FarmCreate.init()