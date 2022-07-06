from utils import config
from pydantic import EmailStr, BaseModel
from typing import List
from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from pathlib import Path

class EmailSchema(BaseModel):
   email: List[EmailStr]

conf = ConnectionConfig(
    MAIL_USERNAME = config.MAIL_USERNAME,
    MAIL_PASSWORD = config.MAIL_PASSWORD,
    MAIL_FROM = config.MAIL_FROM,
    MAIL_PORT = config.MAIL_PORT,
    MAIL_SERVER = config.MAIL_SERVER,
    MAIL_TLS = config.MAIL_TLS,
    MAIL_SSL = config.MAIL_SSL,
    TEMPLATE_FOLDER = Path(__file__).parent / 'templates',
)

async def send_activation_email(email: str, body: dict):

    message = MessageSchema(
        
        subject="Activate Your Email",
        recipients=[email],  # List of recipients, as many as you can pass
        template_body=body
        )
 
    fm = FastMail(conf)
    await fm.send_message(message, template_name="activation_email.html")

async def send_reset_password_email(email: str, body: dict):
    message = MessageSchema(
        
        subject="Reset Your Password",
        recipients=[email],  # List of recipients, as many as you can pass
        template_body=body
        )
 
    fm = FastMail(conf)
    await fm.send_message(message, template_name="reset_password_email.html")