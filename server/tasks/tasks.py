from pydantic import EmailStr
import smtplib
from email.message import EmailMessage
from celery import Celery

from .smtp_config import settings

celery_app = Celery('tasks', broker=f"{settings.BROKER_HOST}:{settings.BROKER_PORT}")


def get_welcome_message(email: str, password: str):
    message = EmailMessage()
    message["Subject"] = settings.NAME
    message["From"] = settings.SMTP_USER
    message["To"] = email

    message.set_content(
        '<div>'
        f'<h3>Здравствуйте, {EmailStr(email).split("@")[0]}</h3>'
        f'<p>Вам были выданы права редактора на сайте {settings.NAME}.</p>'
        f'<p>Ваш логин: {email}</p>'
        f'<p>Ваш пароль: {password}</p>'
        '</div>',
        subtype='html'
    )
    return message


@celery_app.task
def send_welcome_message(email: str, password: str):
    message = get_welcome_message(email, password)
    smtp = smtplib.SMTP_SSL if settings.SMTP_SSL else smtplib.SMTP
    with smtp(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_TLS:
            server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message)
