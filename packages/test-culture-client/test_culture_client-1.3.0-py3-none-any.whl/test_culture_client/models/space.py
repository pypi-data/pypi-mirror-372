from datetime import datetime
from pydantic import BaseModel

from .common import Id


class Space(BaseModel):
    id: Id
    type: Id
    name: str
    createdBy: str
    createdAt: datetime
    updatedBy: str
    updatedAt: datetime
    deleted: bool
