from pydantic import BaseModel
from .common import Id


class CreateTestRunRequest(BaseModel):
    testCaseId: Id
    testCycleId: Id
    
class UpdateTestRunStatusRequest(BaseModel):
    status: str
