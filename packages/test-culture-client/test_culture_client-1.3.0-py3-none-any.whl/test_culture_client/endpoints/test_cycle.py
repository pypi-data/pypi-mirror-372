from test_culture_client.endpoints import EndpointTemplate
from test_culture_client.endpoints.unit import Paths as UnitPaths
from test_culture_client.models.test_cycle import TestCycleRequest


class Paths:
    UNIT_TYPE = "test_cycle"


class TestCycleEndpoint(EndpointTemplate):

    def create(self, json: TestCycleRequest) -> dict:
        return self._client.post(
            UnitPaths.CREATE.format(suit=Paths.UNIT_TYPE), json=json
        )

    def update(self, code: str, json: TestCycleRequest) -> dict:
        return self._client.patch(UnitPaths.UPDATE.format(code=code), json=json)

    def get(self, code: str) -> dict:
        return self._client.get(UnitPaths.GET.format(code=code))
