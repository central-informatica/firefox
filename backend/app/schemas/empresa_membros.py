from pydantic import BaseModel
from datetime import datetime

class EmpresaMembroBase(BaseModel):
    empresa_id: int
    usuario_id: int
    papel: str

class EmpresaMembroCreate(EmpresaMembroBase):
    pass

class EmpresaMembroUpdate(BaseModel):
    papel: str | None = None

class EmpresaMembroOut(EmpresaMembroBase):
    membro_id: int
    criado_em: datetime

    class Config:
        orm_mode = True
