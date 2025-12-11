from pydantic import BaseModel
from typing import Optional


class GrupoCertBase(BaseModel):
    empresa_id: int
    grupo_id: int
    certificado_id: int


class GrupoCertCreate(GrupoCertBase):
    pass


class GrupoCertUpdate(BaseModel):
    empresa_id: Optional[int] = None
    grupo_id: Optional[int] = None
    certificado_id: Optional[int] = None


class GrupoCertOut(GrupoCertBase):
    grupo_cert_id: int

    class Config:
        orm_mode = True
