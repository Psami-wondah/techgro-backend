from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from models.user import User
from routes.auth import auth

app = FastAPI(
    title="Techgro",
    description="Techgro Apis",
    version="1.0.0",
)

app.include_router(auth)

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