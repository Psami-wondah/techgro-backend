from fastapi import Depends, FastAPI, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from models.user import UserInDB
from models.token import TokenData
from jose import JWTError, jwt
from db.config import db
from datetime import datetime, timedelta
from typing import Optional
from serializers.serializers import serialize_dict
from utils import config


oauthroute = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(email: str):
    user = db.users.find_one({"email": email})
    if user:
        return UserInDB(**serialize_dict(user))

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_sio_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return False
        token_data = TokenData(email=email)
    except JWTError:
        return False
    user = get_user(email=token_data.email)
    if user is None:
        return False
    return user


async def verify_user_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


