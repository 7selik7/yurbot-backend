import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from app.core.config import settings
from app.schemas.smtp_schemas import SMTPMessage


class SMTPService:
    def __init__(self):

        pass

    def _create_message(self, msg: SMTPMessage) -> MIMEMultipart:
        message = MIMEMultipart()
        message["From"] = settings.EMAIL_EMAIL
        message["To"] = ",".join(msg.target_emails)
        message["Subject"] = msg.title
        message["Date"] = formatdate(localtime=True)
        message.attach(MIMEText(msg.body, msg.content_type))
        return message

    async def send(self, msg: SMTPMessage) -> None:
        message = self._create_message(msg=msg)
        try:
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_EMAIL, settings.EMAIL_PASSWORD)
                server.sendmail(settings.EMAIL_EMAIL, msg.target_emails, message.as_string())
            print(f"Email sent to {msg.target_emails}")
        except Exception as e:
            print(f"Failed to send email. {e}")
