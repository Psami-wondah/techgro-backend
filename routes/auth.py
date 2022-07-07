from typing import Optional
from fastapi import APIRouter, Form
from models.token import Token
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from oauth.auth import authenticate_user, create_access_token, get_password_hash, get_user
from fastapi.responses import JSONResponse
from fastapi import status
from datetime import timedelta, datetime
from utils import config
from models.auth import GoogleAuth, LoginRes, UserLogin, UserReg, RegRes, ResetPassword
from db.config import db
from pymongo.errors import DuplicateKeyError
from fastapi_mail.errors import ConnectionErrors
from mail.config import send_activation_email, send_reset_password_email
from serializers.serializers import serialize_dict
from jose import JWTError, jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

auth = APIRouter(
    tags=["Auth 🔐"],
    prefix="/api/v1/auth"
)

class OAuth2PasswordRequestFormEmail:
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        email: str = Form(),
        password: str = Form(),
        scope: str = Form(default=""),
        client_id: Optional[str] = Form(default=None),
        client_secret: Optional[str] = Form(default=None),
    ):
        self.grant_type = grant_type
        self.email = email
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


@auth.post("/token", response_model=Token)
async def login_for_access_token(data: OAuth2PasswordRequestFormEmail = Depends()):
    user = authenticate_user(data.email, data.password)
    if not user:
        return JSONResponse(
            {"message": "Incorrect email or password"},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_verified == False:
        return JSONResponse(
            {"message": "email not verified"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires": f"{config.ACCESS_TOKEN_EXPIRE_MINUTES}",
    }


@auth.post("/login", response_model=LoginRes)
async def login(data: UserLogin):
    user = authenticate_user(data.email, data.password)
    if not user:
        return JSONResponse(
            {"message": "Incorrect email or password"},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_verified == False:
        return JSONResponse(
            {"message": "email not verified"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"message": "Login Successful", "user": user, "access_token": access_token}


@auth.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=RegRes
)
async def create_user(reg: UserReg):
    if db.users.find_one({"email": reg.email}):
        return JSONResponse(
            {"message": "email already exists"}, status_code=status.HTTP_400_BAD_REQUEST
        )
    data = {
        "first_name": reg.first_name,
        "last_name": reg.last_name,
        "email": reg.email,
        "hashed_password": get_password_hash(reg.password),
        "image_url": reg.image_url,
        "is_verified": False,
        "created_at": datetime.now(),
    }

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": reg.email}, expires_delta=access_token_expires
    )
    try:
        db.users.insert_one(data)
    except DuplicateKeyError:
        return JSONResponse(
            {"message": "username or email already exists"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        await send_activation_email(
            reg.email,
            {"url": config.BACKEND_URL, "username": reg.username, "token": access_token},
        )

    except ConnectionErrors:
        return JSONResponse(
            {"message": "failed to send email due to smtp connection errors"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return {
        "message": "Registration succesful, check email",
    }



@auth.post(
    "/resend-verification-email/{email}", status_code=status.HTTP_200_OK
)
async def resend_verification_email(email: str):
    user = db.users.find_one({"email": email})
    if user:

        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        user = serialize_dict(db.users.find_one({"email": email}))
        if user["is_verified"]:
            return JSONResponse(
                {"message": "user already verified"},
                status_code=status.HTTP_208_ALREADY_REPORTED,
            )
        try:
            await send_activation_email(
                email,
                {
                    "url": config.BACKEND_URL,
                    "token": access_token,
                },
            )

        except ConnectionErrors as e:
            return JSONResponse(
                {"message": f"failed to send email due to smtp connection errors: {e}"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return {"message": "verification email sent"}
    else:
        return JSONResponse(
            {"message": "email doesn't exist"}, status_code=status.HTTP_400_BAD_REQUEST
        )

@auth.post("/verify-email/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return JSONResponse(
                {"message": "verification failed, token expired"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        verification = {"is_verified": True}
        if db.users.find_one({"email": email}):
            db.users.find_one_and_update({"email": email}, {"$set": verification})
            return {"message": "verification succesful"}
        else:
            return {"message": f"email: {email} doesn't exist in our database"}
    except JWTError:
        return JSONResponse(
            {"message": "verification failed, token expired"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@auth.post("/forgot-password/{email}", status_code=status.HTTP_200_OK)
async def forgot_password(email: str):
    user = db.users.find_one({"email": email})
    if user:
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        try:
            await send_reset_password_email(
                email,
                {
                    "url": config.BACKEND_URL,
                    "username": user["username"],
                    "token": access_token,
                },
            )

        except ConnectionErrors:
            return JSONResponse(
                {"message": "failed to send email due to smtp connection errors"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return {"message": "reset password email sent"}
    else:
        return JSONResponse(
            {"message": f"user with email {email} doesn't exist"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@auth.put("/reset-password/{token}", status_code=status.HTTP_200_OK)
async def reset_password(token: str, reset: ResetPassword):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return JSONResponse(
                {"message": "reset password failed, token expired"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        data = {"hashed_password": get_password_hash(reset.password)}
        db.users.find_one_and_update({"email": email}, {"$set": data})
    except JWTError:
        return JSONResponse(
            {"message": "reset password failed, token expired"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return {"message": "password reset succesful"}


@auth.post("/google", response_model=LoginRes)
async def google_auth(data: GoogleAuth):
    try:
        user_data = id_token.verify_oauth2_token(
            data.credential,
            google_requests.Request(),
            config.GOOGLE_CLIENT_ID,
        )
        email = user_data["email"]
        user = get_user(email)
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
        if user:
            if not user.is_verified:
                verification = {"is_verified": True}
                db.users.find_one_and_update({"email": email}, {"$set": verification})
            return {"message": "Login with Google Successful", "user": user, "access_token": access_token}
        data = {
        "username": email,
        "first_name": user_data.get("given_name"),
        "last_name": user_data.get("family_name"),
        "email": email,
        "hashed_password": get_password_hash("9d32af9da9df2e4777116f79ae3516bc799be0d6c82702afcfc6ba7d6104b69d"),
        "image_url": user_data.get("picture"),
        "is_verified": True,
        "created_at": datetime.now(),
        }
        try:
            db.users.insert_one(data)
        except DuplicateKeyError:
            return JSONResponse(
                {"message": "username or email already exists"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return {"message": "Registration with Google Successful", "user": user, "access_token": access_token}

    except ValueError:
            return JSONResponse(
                {"message": "Invalid token"}, status_code=status.HTTP_400_BAD_REQUEST
        )