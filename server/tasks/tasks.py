import os
import sys

from jinja2 import Environment, FileSystemLoader

from pydantic import EmailStr
import smtplib
from email.message import EmailMessage
from celery import Celery

server_path = os.path.join(os.getcwd(), "")
sys.path.insert(0, server_path)
from config import settings

celery_app = Celery('tasks', broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")

path_to_templates = './templates/tasks/'


def message_generator(email: EmailStr, content: str, subject: str = settings.NAME, subtype='html'):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.SMTP_USER
    message["To"] = email
    message.set_content(content, subtype=subtype)
    return message


def templater(template, **kwargs):
    env = Environment(loader=FileSystemLoader(path_to_templates))
    template = env.get_template(template)
    html_content = template.render(**kwargs)

    return html_content


def send_message(message):
    smtp = smtplib.SMTP_SSL if settings.SMTP_SSL else smtplib.SMTP
    with smtp(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_TLS:
            server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message)


def welcome_message(email: EmailStr, password: str):
    username = email.split("@")[0]
    html_content = templater('welcome.html', email=email, password=password, username=username, settings=settings)
    return message_generator(email, html_content)


def newsletter(email: EmailStr, token: str, unfollow_link, news: dict):
    html_content = templater('newsletter.html', news=news, token=token, unfollow_link=unfollow_link)
    return message_generator(email, html_content, subject=news["title"])


@celery_app.task
def send_welcome_message(email: EmailStr, password: str):
    message = welcome_message(email, password)
    send_message(message)


@celery_app.task
def send_newsletter_for_email(email: EmailStr, token: str, unfollow_link: str, news: dict):
    message = newsletter(email, token, unfollow_link, news)
    send_message(message)
