from pydantic import EmailStr
import smtplib
from email.message import EmailMessage
from celery import Celery

from .smtp_config import settings

celery_app = Celery('tasks', broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")


def message_generator(email: EmailStr, content: str, subject: str = settings.NAME, subtype='html'):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.SMTP_USER
    message["To"] = email
    message.set_content(content, subtype=subtype)
    return message


def send_message(message):
    smtp = smtplib.SMTP_SSL if settings.SMTP_SSL else smtplib.SMTP
    with smtp(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_TLS:
            server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message)


def welcome_message(email: EmailStr, password: str):
    return message_generator(email,
                             '<div>'
                             f'<h3>Здравствуйте, {email.split("@")[0]}</h3>'
                             f'<p>Вам были выданы права редактора на сайте {settings.NAME}.</p>'
                             f'<p>Ваш логин: {email}</p>'
                             f'<p>Ваш пароль: {password}</p>'
                             '</div>')


def newsletter(email: EmailStr, news: dict):
    return message_generator(email,
                             '<div>'
                             f'<h1>{news["title"]}</h1>'
                             f'<h2>{news["description"]}</h3>'
                             '<br>'
                             f'<p>{news["content"]}</p>',
                             subject=news["title"])


@celery_app.task
def send_welcome_message(email: EmailStr, password: str):
    message = welcome_message(email, password)
    send_message(message)


@celery_app.task
def send_newsletter_for_email(email: EmailStr, news: dict):
    message = newsletter(email, news)
    send_message(message)
