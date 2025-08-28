from typing import Literal, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class FormattedText(BaseModel):
    plainText: Optional[str]
    formattedText: Optional[str]


class FileMetadataDto(BaseModel):
    contentType: str
    contentLength: int


class CreatedBy(BaseModel):
    externalId: str
    firstName: str
    lastName: str
    middleName: str
    login: str
    locale: str


class FilePathParsedDto(BaseModel):
    relatedToType: str
    relativePath: str
    fileName: str


class File(BaseModel):
    fileId: UUID
    filePathParsedDto: FilePathParsedDto
    createdBy: CreatedBy
    createdAt: datetime
    fileMetadataDto: FileMetadataDto


class TestCaseStepItem(BaseModel):
    stepNumber: int
    deleted: bool = False
    code: Optional[str] = None
    stepDescription: Optional[FormattedText] = None
    stepData: Optional[FormattedText] = None
    stepResult: Optional[FormattedText] = None
    stepFiles: Optional[list[File]] = []
    callToTestId: Optional[str] = None


class TestCaseSteps(BaseModel):
    testStepList: list[TestCaseStepItem]


class TestCaseAttributes(BaseModel):
    priority: str
    type_of_testing: str
    test_type: str
    test_case_status: str
    folder: str
    pmi: Literal["yes", "not"]
    precondition: Optional[str] = None
    owner: Optional[str] = None
    automated: Optional[str] = None
    label: Optional[list[str]] = None
    test_step: Optional[TestCaseSteps] = None
    component_code: Optional[str] = None
    component_version: Optional[str] = None
    test_level: Optional[str] = None
    product_code: Optional[str] = None
    product_version: Optional[str] = None
    estimate: Optional[str] = None


class BaseTestCaseRequest(BaseModel):
    summary: str
    description: Optional[str] = None
    attributes: TestCaseAttributes


class TestCaseCreateRequest(BaseTestCaseRequest):
    space: str


class TestCaseUpdateRequest(BaseTestCaseRequest):
    suit: str = "test_case"
