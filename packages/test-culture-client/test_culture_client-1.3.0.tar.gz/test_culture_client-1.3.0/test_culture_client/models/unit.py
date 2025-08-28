from datetime import datetime
from pydantic import BaseModel
from typing import List, Any

from .common import Id

class UnitAttributeTypeId(BaseModel):
    code: str


class UnitAttributeType(BaseModel):
    id: UnitAttributeTypeId
    name: str
    description: str


class UnitAttributeId(BaseModel):
    code: str


class UnitAttribute(BaseModel):
    id: UnitAttributeId
    name: str
    type: UnitAttributeTypeId
    description: str


class Unit(BaseModel):
    id: Id
    space: Id
    summary: str
    description: str
    suit: Id
    createdBy: str
    createdAt: datetime
    updatedBy: str
    updatedAt: datetime
    deleted: bool
    
class UnitAttributeValueModRequest(BaseModel):
    id: UnitAttributeId
    value: Any


class UnitModRequest(BaseModel):
    summary: str
    description: str
    space: Id
    attributes: List[UnitAttributeValueModRequest]
    