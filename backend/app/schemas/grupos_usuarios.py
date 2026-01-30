from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class GrupoUsuarioBase(BaseModel):
    grupo_id: UUID


class GrupoUsuarioCreate(GrupoUsuarioBase):
    usuario_id: str
    empresa_id: Optional[str] = None


class GrupoUsuarioUpdate(BaseModel):
    grupo_id: Optional[UUID] = None


class GrupoUsuarioOut(GrupoUsuarioBase):
    grupo_usuario_id: UUID

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
