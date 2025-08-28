from test_culture_client.endpoints import EndpointTemplate
from test_culture_client.models.link import UnitLinkRequest
from test_culture_client.models.tql import TqlRequest
from test_culture_client.models.unit import UnitModRequest


class Paths:
    # POST Создает новый юнит с заданным типом атрибута
    CREATE = "/rest/api/unit/v2/{suit}/create"
    # PATCH Обновляет существующий юнит по его коду
    UPDATE = "/rest/api/unit/v2/update/{code}"
    # GET Получение юнита по его коду
    GET = "/rest/api/unit/v2/{code}"
    # POST Запрос на получение постраничного списка юнитов с помощью TQL
    FIND_BY_TQL = "/rest/api/unit/v2/find/tql"
    # POST Запрос на создание связи юнита
    ADD_LINK = "/rest/api/unit/v1/link"
    # DELETE Запрос на удаление связи юнита
    DELETE_LINK = "/rest/api/unit/v1/link/delete"


class UnitEndpoint(EndpointTemplate):

    def create(self, suit: str, json: UnitModRequest) -> dict:
        return self._client.post(Paths.CREATE.format(suit=suit), json=json)

    def update(self, code: str, json: UnitModRequest) -> dict:
        return self._client.patch(Paths.UPDATE.format(code=code), json=json)

    def get(self, code: str) -> dict:
        return self._client.get(Paths.GET.format(code=code))

    def find_by_tql(self, json: TqlRequest) -> dict:
        return self._client.post(Paths.FIND_BY_TQL, json=json)

    def link(self, json: UnitLinkRequest) -> dict:
        return self._client.post(Paths.ADD_LINK, json=json)

    def unlink(self, json: UnitLinkRequest) -> dict:
        return self._client.delete(Paths.DELETE_LINK, json=json)
