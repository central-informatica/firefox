from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginJSON(BaseModel):
    email: EmailStr
    senha: str


class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    telefone: Optional[str] = None  


class UserOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    empresa_id: Optional[int] = None

    class Config:
        orm_mode = True
