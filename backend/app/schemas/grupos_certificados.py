from pydantic import BaseModel
from typing import Optional


class GrupoCertBase(BaseModel):
    grupo_id: str


class GrupoCertCreate(GrupoCertBase):
    pass


class GrupoCertUpdate(BaseModel):
    grupo_id: Optional[str] = None


class GrupoCertOut(GrupoCertBase):
    grupo_cert_id: str

    class Config:
        orm_mode = True
