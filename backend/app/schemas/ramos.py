from pydantic import BaseModel
from typing import Optional


class RamoBase(BaseModel):
    ramo: str


class RamoCreate(RamoBase):
    pass


class RamoUpdate(BaseModel):
    ramo: Optional[str] = None


class RamoOut(RamoBase):
    ramos_id: int

    class Config:
        orm_mode = True
