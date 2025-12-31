from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional


class EmpresaBase(BaseModel):
    razao_social: constr(min_length=2, max_length=120)
    fantasia: Optional[str] = None
    cnpj: constr(min_length=14, max_length=14)
    timezone: Optional[str] = "America/Sao_Paulo"


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaUpdate(BaseModel):
    razao_social: Optional[str] = None
    fantasia: Optional[str] = None
    timezone: Optional[str] = None


class EmpresaOut(EmpresaBase):
    empresa_id: int
    anfitria_usuario_id: int
    criado_em: datetime

    class Config:
        orm_mode = True
