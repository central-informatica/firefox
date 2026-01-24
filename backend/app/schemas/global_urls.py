from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GlobalUrlBase(BaseModel):
    url: Optional[str] = None
    inativo: Optional[bool] = False
    empresa_id: str


class GlobalUrlCreate(GlobalUrlBase):
    pass


class GlobalUrlUpdate(BaseModel):
    url: Optional[str] = None
    inativo: Optional[bool] = None


class GlobalUrlOut(GlobalUrlBase):
    global_urls_id: str
    criado_em: Optional[datetime] = None

    class Config:
        orm_mode = True
