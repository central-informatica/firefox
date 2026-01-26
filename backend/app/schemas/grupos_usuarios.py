from pydantic import BaseModel
from typing import Optional


class GrupoUsuarioBase(BaseModel):
    grupo_id: str


class GrupoUsuarioCreate(GrupoUsuarioBase):
    usuario_id: str
    empresa_id: Optional[str] = None


class GrupoUsuarioUpdate(BaseModel):
    grupo_id: Optional[str] = None


class GrupoUsuarioOut(GrupoUsuarioBase):
    grupo_usuario_id: str

    class Config:
        orm_mode = True


class GrupoUsuarioBulkCreate(BaseModel):
    grupo_id: str
    usuario_ids: list[str]
    empresa_id: Optional[str] = None


class GrupoUsuarioBulkSkipped(BaseModel):
    usuario_id: str
    reason: str


class GrupoUsuarioBulkResult(BaseModel):
    created: list[str]
    skipped: list[GrupoUsuarioBulkSkipped]
