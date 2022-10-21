import requests
from utils import config
from fastapi.templating import Jinja2Templates


from pathlib import Path
BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH.joinpath("templates")))

headers = {"api-key": config.SENDINBLUE_API_KEY}


def send_activation_email(email, body):
    template = templates.get_template("activation_email.html")
    body = {
        "sender": {"name": "Techgro", "email": "support@techgro.ng"},
        "to": [{"email": email, "name": email}],
        "subject": "Activate Your Email",
        "htmlContent": template.render(body),
    }
    response = requests.post(
        "https://api.sendinblue.com/v3/smtp/email", headers=headers, json=body
    )
    if response.status_code == 201:
        return True
    return False

def send_reset_password_email(email: str, body: dict):
    template = templates.get_template("reset_password_email.html")
    body = {
        "sender": {"name": "Techgro", "email": "support@techgro.ng"},
        "to": [{"email": email, "name": email}],
        "subject": "Reset Your Password",
        "htmlContent": template.render(body),
    }
    response = requests.post(
        "https://api.sendinblue.com/v3/smtp/email", headers=headers, json=body
    )
    if response.status_code == 201:
        return True
    return False 
