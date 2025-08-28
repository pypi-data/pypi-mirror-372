from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID


class TestCaseParameterRequestId(BaseModel):
    parameterId: Optional[UUID] = None


class TestCaseParameter(BaseModel):
    id: Optional[TestCaseParameterRequestId] = None
    order: int
    name: str
    value: str


class TestCaseParametersRequest(BaseModel):
    parameters: List[TestCaseParameter]
