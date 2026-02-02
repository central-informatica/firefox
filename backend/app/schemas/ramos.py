from pydantic import BaseModel, ConfigDict
from typing import Optional


class RamoBase(BaseModel):
    ramo: str


class RamoCreate(RamoBase):
    pass


class RamoUpdate(BaseModel):
    ramo: Optional[str] = None


class RamoOut(RamoBase):
    ramos_id: str

    model_config = ConfigDict(from_attributes=True)
