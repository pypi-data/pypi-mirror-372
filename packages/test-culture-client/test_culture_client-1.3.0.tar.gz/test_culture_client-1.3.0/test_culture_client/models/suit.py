from typing import List
from pydantic import BaseModel

from .unit import UnitAttribute
from .common import Id

class Suit(BaseModel):
    id: Id
    name: str
    description: str
    icon: str
    deleted: bool
    attributes: List[UnitAttribute]
