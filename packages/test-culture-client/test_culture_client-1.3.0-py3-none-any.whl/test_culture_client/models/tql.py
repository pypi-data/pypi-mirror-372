from typing import Optional, List
from pydantic import BaseModel, Field, conint


class PageRequest(BaseModel):
    """Параметры пагинации"""

    page: conint(ge=0) = Field(..., description="Номер страницы")
    size: conint(ge=1) = Field(..., description="Размер страницы")


class TqlRequest(BaseModel):
    """Запрос TQL (Test Query Language)"""

    query: str = Field(..., description="TQL запрос")
    attributes: Optional[List[str]] = Field(
        None, description="Список атрибутов для включения в ответ"
    )
    page: Optional[PageRequest] = Field(None, description="Параметры пагинации")
