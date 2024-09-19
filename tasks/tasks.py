import smtplib
from email.message import EmailMessage
from celery import Celery
from app.auth.config import settings

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD

celery = Celery('tasks', broker='redis://localhost:6380/0')

celery.conf.broker_transport_options = {'visibility_timeout': 3600}



def get_email_template_dashboard(username: str, recipient_email: str):
    email = EmailMessage()
    email['Subject'] = 'Добро пожаловать!'
    email['From'] = SMTP_USER
    email['To'] = recipient_email



    email.set_content(f"Здравствуйте, {username}, добро пожаловать!", subtype="plain")
    return email


@celery.task
def send_email_report_dashboard(username: str, recipient_email: str):
    email = get_email_template_dashboard(username, recipient_email)


    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)