from test_culture_client.endpoints import TMS_PLUGIN_API_PREFIX, EndpointTemplate
from test_culture_client.models.test_case.entry import TestCaseCreateRequest, TestCaseUpdateRequest
from test_culture_client.endpoints.unit import Paths as UnitPaths
from test_culture_client.models.test_case.parameter import TestCaseParametersRequest
from test_culture_client.models.test_case.data import TestCaseDataRequest


class Paths:
    UNIT_TYPE = "test_case"

    # POST Сохранение тест-данных тест-кейса
    SET_TEST_DATA = "%s/test_case/{unit_id}/test_data" % TMS_PLUGIN_API_PREFIX
    # POST Сохранение параметров тест-кейса
    SET_PARAMETERS = "%s/test_case/{unit_id}/parameters" % TMS_PLUGIN_API_PREFIX


class TestCaseEndpoint(EndpointTemplate):

    def create(self, json: TestCaseCreateRequest) -> dict:
        return self._client.post(
            UnitPaths.CREATE.format(suit=Paths.UNIT_TYPE), json=json
        )

    def update(self, code: str, json: TestCaseUpdateRequest) -> dict:
        return self._client.patch(UnitPaths.UPDATE.format(code=code), json=json)

    def get(self, code: str) -> dict:
        return self._client.get(UnitPaths.GET.format(code=code))

    def update_test_data(self, unit_id: str, json: TestCaseDataRequest) -> dict:
        return self._client.post(Paths.SET_TEST_DATA.format(unit_id=unit_id), json=json)

    def update_parameters(self, unit_id: str, json: TestCaseParametersRequest) -> dict:
        return self._client.post(
            Paths.SET_PARAMETERS.format(unit_id=unit_id), json=json
        )
