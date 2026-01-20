from pydantic import BaseModel
from typing import Optional


class GrupoCertBase(BaseModel):
    grupo_id: int


class GrupoCertCreate(GrupoCertBase):
    pass


class GrupoCertUpdate(BaseModel):
    grupo_id: Optional[int] = None


class GrupoCertOut(GrupoCertBase):
    grupo_cert_id: int

    class Config:
        orm_mode = True
