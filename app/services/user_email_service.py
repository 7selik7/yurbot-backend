from jinja2 import Environment, FileSystemLoader


from app.schemas.smtp_schemas import SMTPMessage
from app.services.smtp_service import SMTPService


class UserEmailService:
    def __init__(self) -> None:
        self.smtp = SMTPService()
        self.template_env = Environment(loader=FileSystemLoader(searchpath="templates"))

    async def _send_email(self, title: str, email: str, template_name: str, context: dict) -> None:
        template = self.template_env.get_template(template_name)
        rendered_html = template.render(**context)

        msg = SMTPMessage(
            title=title,
            target_emails=[email],
            body=rendered_html,
            content_type="html",
        )
        print(f"Send '{title}' email to {email}")
        await self.smtp.send(msg=msg)


    async def send_signup_confirmation(self, email: str, url: str) -> None:
        await self._send_email(
            title="Confirmation of Registration",
            email=email,
            template_name="signup_confirm.html",
            context={"url": url},
        )

    async def send_reset_password(self, email: str, url: str) -> None:
        await self._send_email(
            title="PathSearch Password Reset",
            email=email,
            template_name="reset_password.html",
            context={"url": url},
        )


user_email_service = UserEmailService()
