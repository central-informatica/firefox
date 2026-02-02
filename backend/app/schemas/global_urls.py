from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class GlobalUrlBase(BaseModel):
    url: Optional[str] = None
    inativo: Optional[bool] = False
    empresa_id: UUID


class GlobalUrlCreate(GlobalUrlBase):
    pass


class GlobalUrlUpdate(BaseModel):
    url: Optional[str] = None
    inativo: Optional[bool] = None


class GlobalUrlOut(GlobalUrlBase):
    global_urls_id: UUID
    criado_em: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
