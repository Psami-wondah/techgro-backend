import os
from dotenv import load_dotenv
load_dotenv()



SECRET_KEY = os.getenv('SECRET_KEY')
MONGO_URI = os.getenv('MONGO_URI')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_FROM = os.getenv('MAIL_FROM')
MAIL_PORT = int(os.getenv('MAIL_PORT'))
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_TLS = os.getenv('MAIL_TLS')
MAIL_SSL = os.getenv('MAIL_SSL')
REDIS_URL = os.getenv('REDIS_URL')
BACKEND_URL = os.getenv('BACKEND_URL')
SECRET_KEY = str(SECRET_KEY)
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
SENDINBLUE_API_KEY=os.getenv("SENDINBLUE_API_KEY")