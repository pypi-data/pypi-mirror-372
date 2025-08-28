from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class TestCaseDataId(BaseModel):
    parameterId: Optional[UUID] = None


class TestCaseDataValue(BaseModel):
    order: int
    value: str


class TestCaseDataEntry(BaseModel):
    id: Optional[TestCaseDataId] = None
    order: int
    name: str
    value: list[TestCaseDataValue]


class TestCaseDataRequest(BaseModel):
    data: list[TestCaseDataEntry]
