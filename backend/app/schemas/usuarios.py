from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    nome: constr(min_length=2, max_length=80)
    email: EmailStr
    telefone: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    # Campo de senha em texto puro apenas para entrada;
    # o CRUD continua responsável por gerar o senha_hash.
    senha: constr(min_length=6)


class UsuarioUpdate(BaseModel):
    nome: Optional[constr(min_length=2, max_length=80)] = None
    telefone: Optional[str] = None
    senha: Optional[constr(min_length=6)] = None


class UsuarioOut(UsuarioBase):
    usuario_id: int
    email_verificado: bool
    criado_em: datetime
    atualizado_em: datetime
    nivel: str

    class Config:
        orm_mode = True

class UsuariosPaginadoOut(BaseModel):
    data: list[UsuarioOut]
    total: int
    total_adm: int

    class Config:
        orm_mode = True

class EmpresaDoUsuarioOut(BaseModel):
    empresa_id: int
    razao_social: str
    fantasia: Optional[str] = None
    cnpj: str
    timezone: str

    class Config:
        orm_mode = True
