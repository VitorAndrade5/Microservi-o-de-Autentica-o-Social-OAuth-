from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSchema(BaseModel):
    email: EmailStr
    name: str
    provider: str


class CredentialSchema(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
