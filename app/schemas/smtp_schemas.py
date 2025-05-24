from pydantic import BaseModel, Field, EmailStr



class SMTPMessage(BaseModel):
    title: str
    target_emails: list[EmailStr] = []
    body: str
    content_type: str = "plain"
