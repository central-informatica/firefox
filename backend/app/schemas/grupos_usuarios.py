from pydantic import BaseModel
from typing import Optional


class GrupoUsuarioBase(BaseModel):
    grupo_id: int


class GrupoUsuarioCreate(GrupoUsuarioBase):
    pass


class GrupoUsuarioUpdate(BaseModel):
    grupo_id: Optional[int] = None


class GrupoUsuarioOut(GrupoUsuarioBase):
    grupo_usuario_id: int

    class Config:
        orm_mode = True
