from typing import Literal, Optional
from pydantic import BaseModel


class TestCycleAttributes(BaseModel):
    folder: str
    test_cycle_status: str
    type_of_testing: str
    test_case_test_type: str
    cycles_number: str
    plan_date_start: Optional[str] = None
    plan_date_end: Optional[str] = None
    owner: Optional[str] = None
    release_name: Optional[str] = None
    iteration_type: Optional[str] = None
    old_jira_key: Optional[str] = None
    cycle_automated: Optional[Literal["yes", "not"]] = None


class TestCycleRequest(BaseModel):
    summary: str
    description: str
    space: str
    attributes: TestCycleAttributes
