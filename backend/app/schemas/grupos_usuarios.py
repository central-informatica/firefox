from pydantic import BaseModel
from typing import Optional


class GrupoUsuarioBase(BaseModel):
    empresa_id: int
    grupo_id: int
    usuario_id: int


class GrupoUsuarioCreate(GrupoUsuarioBase):
    pass


class GrupoUsuarioUpdate(BaseModel):
    empresa_id: Optional[int] = None
    grupo_id: Optional[int] = None
    usuario_id: Optional[int] = None


class GrupoUsuarioOut(GrupoUsuarioBase):
    grupo_usuario_id: int

    class Config:
        orm_mode = True


class GrupoUsuarioBulkCreate(BaseModel):
    grupo_id: int
    usuario_ids: list[int]
    empresa_id: Optional[int] = None


class GrupoUsuarioBulkSkipped(BaseModel):
    usuario_id: int
    reason: str


class GrupoUsuarioBulkResult(BaseModel):
    created: list[int]
    skipped: list[GrupoUsuarioBulkSkipped]
