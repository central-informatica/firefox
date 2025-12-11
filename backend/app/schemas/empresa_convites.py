from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID


class EmpresaConviteBase(BaseModel):
    empresa_id: int
    email_convidado: EmailStr


class EmpresaConviteCreate(EmpresaConviteBase):
    pass


class EmpresaConviteUpdate(BaseModel):
    status: Optional[str] = None
    convidado_usuario_id: Optional[int] = None


class EmpresaConviteOut(EmpresaConviteBase):
    convite_id: int
    convite_uuid: UUID
    status: str
    expiracao: datetime
    criado_em: datetime

    class Config:
        orm_mode = True
