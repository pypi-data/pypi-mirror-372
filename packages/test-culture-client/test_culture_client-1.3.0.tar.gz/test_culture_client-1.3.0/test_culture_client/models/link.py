from pydantic import BaseModel


class UnitLinkRequest(BaseModel):
    """
    Запрос на создание связи между юнитами
    """

    source: str
    destination: str
    type: str
